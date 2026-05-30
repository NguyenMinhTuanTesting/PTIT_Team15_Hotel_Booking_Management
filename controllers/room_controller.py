import threading
import time
from utils.db_helper import DatabaseHelper

class RoomController:
    def __init__(self):
        self.db = DatabaseHelper()
        self.start_auto_cleaner()

    def start_auto_cleaner(self):
        def cleaner_task():
            while True:
                try:
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    query = """
                        UPDATE bookings 
                        SET status = 'COMPLETED' 
                        WHERE status = 'CLEANING' 
                        AND cleaning_start_time IS NOT NULL 
                        AND DATE_ADD(cleaning_start_time, INTERVAL 30 MINUTE) <= NOW()
                    """
                    cursor.execute(query)
                    conn.commit()
                    cursor.close()
                except Exception as e:
                    pass
                time.sleep(60) # Run every 1 minute
                
        t = threading.Thread(target=cleaner_task, daemon=True)
        t.start()

    def get_rooms_status_by_time(self, check_in, check_out, callback):
        def fetch_task():
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor(dictionary=True)
                
                query = """
                    SELECT r.room_id, r.room_number, r.room_type, r.price,
                           b.booking_id, b.status as booking_status,
                           c.first_name, c.last_name
                    FROM rooms r
                    LEFT JOIN bookings b ON r.room_id = b.room_id 
                         AND b.status != 'CANCELLED'
                         AND b.status != 'COMPLETED'
                         AND (
                             (b.status NOT IN ('CHECKED_OUT', 'CLEANING') AND b.check_in_date < %s AND b.check_out_date > %s)
                         OR 
                         (b.status IN ('CHECKED_OUT', 'CLEANING') AND b.check_in_date < %s)
                         )
                    LEFT JOIN customers c ON b.customer_id = c.customer_id
                    ORDER BY r.room_id ASC
                """
                cursor.execute(query, (check_out, check_in, check_out))
                results = cursor.fetchall()
                cursor.close()
                
                rooms_map = {}
                for row in results:
                    rid = row['room_id']
                    if rid not in rooms_map:
                        status = "Trống"
                        if row['booking_status'] == 'MAINTENANCE':
                            status = "Bảo trì"
                        elif row['booking_status'] == 'CHECKED_IN':
                            status = "Đã check in"
                        elif row['booking_status'] == 'CHECKED_OUT':
                            status = "Đã check out"
                        elif row['booking_status'] == 'CLEANING':
                            status = "Đang vệ sinh"
                        elif row['booking_status'] in ('PENDING', 'CONFIRMED'):
                            status = "Đã book"
                            
                        customer_name = ""
                        if row['first_name']:
                            customer_name = f"{row['first_name']} {row['last_name']}"
                            
                        rooms_map[rid] = {
                            "room_id": rid,
                            "room_number": row['room_number'],
                            "room_type": row['room_type'],
                            "price": row['price'],
                            "status": status,
                            "booking_id": row['booking_id'],
                            "customer_name": customer_name
                        }
                
                callback(list(rooms_map.values()))
            except Exception as e:
                print(e)
                callback([])
        threading.Thread(target=fetch_task, daemon=True).start()

    def mark_maintenance(self, room_id, check_in, check_out, callback):
        def task():
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO bookings (customer_id, room_id, check_in_date, check_out_date, status) VALUES (NULL, %s, %s, %s, 'MAINTENANCE')", 
                    (room_id, check_in, check_out)
                )
                conn.commit()
                cursor.close()
                callback(True)
            except Exception as e:
                print(e)
                callback(False)
        threading.Thread(target=task, daemon=True).start()

    def remove_maintenance(self, booking_id, callback):
        def task():
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bookings WHERE booking_id = %s AND status = 'MAINTENANCE'", (booking_id,))
                conn.commit()
                cursor.close()
                callback(True)
            except Exception:
                callback(False)
        threading.Thread(target=task, daemon=True).start()

    def update_booking_status(self, booking_id, new_status, callback):
        def task():
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                if new_status == 'CHECKED_OUT':
                    cursor.execute("UPDATE bookings SET status = %s, actual_check_out_time = NOW() WHERE booking_id = %s", (new_status, booking_id))
                elif new_status == 'CLEANING':
                    cursor.execute("UPDATE bookings SET status = %s, cleaning_start_time = NOW() WHERE booking_id = %s", (new_status, booking_id))
                else:
                    cursor.execute("UPDATE bookings SET status = %s WHERE booking_id = %s", (new_status, booking_id))
                conn.commit()
                cursor.close()
                callback(True)
            except Exception:
                callback(False)
        threading.Thread(target=task, daemon=True).start()
