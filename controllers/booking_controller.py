import threading
from utils.db_helper import DatabaseHelper
from utils.email_sender import send_booking_confirmation

class BookingController:
    def __init__(self):
        self.db = DatabaseHelper()

    def find_available_rooms(self, check_in, check_out, callback):
        def task():
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT * FROM rooms 
                    WHERE room_id NOT IN (
                        SELECT room_id FROM bookings 
                        WHERE status != 'CANCELLED' 
                        AND status != 'COMPLETED'
                        AND (
                            (status NOT IN ('CHECKED_OUT', 'CLEANING') AND check_in_date < %s AND check_out_date > %s)
                            OR 
                            (status IN ('CHECKED_OUT', 'CLEANING') AND check_in_date < %s)
                        )
                    )
                """
                cursor.execute(query, (check_out, check_in, check_out))
                rooms = cursor.fetchall()
                cursor.close()
                callback(rooms)
            except Exception:
                callback([])
        threading.Thread(target=task, daemon=True).start()

    def create_booking(self, first_name, last_name, phone, email, room_id, check_in, check_out, callback):
        def task():
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT customer_id FROM customers WHERE email = %s OR phone = %s", (email, phone))
                customer = cursor.fetchone()
                
                if customer:
                    customer_id = customer[0]
                else:
                    cursor.execute("INSERT INTO customers (first_name, last_name, phone, email) VALUES (%s, %s, %s, %s)", 
                                   (first_name, last_name, phone, email))
                    customer_id = cursor.lastrowid
                    
                cursor.execute(
                    "INSERT INTO bookings (customer_id, room_id, check_in_date, check_out_date, status) VALUES (%s, %s, %s, %s, 'CONFIRMED')",
                    (customer_id, room_id, check_in, check_out)
                )
                booking_id = cursor.lastrowid
                conn.commit()
                cursor.close()
                
                send_booking_confirmation(email, booking_id)
                callback(True)
            except Exception:
                callback(False)
        threading.Thread(target=task, daemon=True).start()
