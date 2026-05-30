import threading
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from utils.db_helper import DatabaseHelper

load_dotenv()

def send_booking_confirmation(email_to, booking_id):
    def task():
        try:
            db = DatabaseHelper()
            conn = db.get_connection()
            if not conn:
                return
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT b.check_in_date, b.check_out_date,
                       c.first_name, c.last_name, c.phone,
                       r.room_number, r.room_type, r.price
                FROM bookings b
                JOIN customers c ON b.customer_id = c.customer_id
                JOIN rooms r ON b.room_id = r.room_id
                WHERE b.booking_id = %s
            """
            cursor.execute(query, (booking_id,))
            data = cursor.fetchone()
            cursor.close()
            
            if not data:
                return
                
            customer_name = f"{data['first_name']} {data['last_name']}"
            check_in = data['check_in_date'].strftime('%H:%M %d-%m-%Y')
            check_out = data['check_out_date'].strftime('%H:%M %d-%m-%Y')
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                    <div style="background-color: #10B981; color: white; padding: 20px; text-align: center;">
                        <h2 style="margin: 0;">Xác Nhận Đặt Phòng Thành Công</h2>
                        <p style="margin: 5px 0 0;">Hotel Management System</p>
                    </div>
                    
                    <div style="padding: 20px;">
                        <p>Kính gửi <strong>{customer_name}</strong>,</p>
                        <p>Cảm ơn bạn đã lựa chọn dịch vụ của chúng tôi. Dưới đây là thông tin chi tiết về phòng bạn đã đặt:</p>
                        
                        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #eee; width: 40%;"><strong>Số điện thoại:</strong></td>
                                <td style="padding: 10px; border-bottom: 1px solid #eee;">{data['phone']}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Phòng:</strong></td>
                                <td style="padding: 10px; border-bottom: 1px solid #eee;">{data['room_number']} (Hạng: {data['room_type']})</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Thời gian Check-in:</strong></td>
                                <td style="padding: 10px; border-bottom: 1px solid #eee; color: #2563EB; font-weight: bold;">{check_in}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Thời gian Check-out:</strong></td>
                                <td style="padding: 10px; border-bottom: 1px solid #eee; color: #EF4444; font-weight: bold;">{check_out}</td>
                            </tr>
                        </table>
                        
                        <p style="text-align: center; margin-top: 30px;">Hệ thống đã ghi nhận lịch của bạn. Hẹn gặp lại bạn tại khách sạn!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = MIMEText(html_content, 'html')
            msg['Subject'] = f'Xác nhận đặt phòng - Mã số #{booking_id:04d}'
            
            mail_user = os.getenv("MAIL_USERNAME")
            mail_pass = os.getenv("MAIL_PASSWORD")
            
            if not mail_user or not mail_pass:
                return
                
            msg['From'] = mail_user
            msg['To'] = email_to
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(mail_user, mail_pass)
                server.send_message(msg)
        except Exception:
            pass
    threading.Thread(target=task, daemon=True).start()
