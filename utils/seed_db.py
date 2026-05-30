import bcrypt
import sys
import os
import mysql.connector
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

def seed():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
    except Exception as e:
        print(f"Không thể kết nối MySQL. Vui lòng kiểm tra MySQL Server đang bật. Lỗi: {e}")
        return
        
    cursor = conn.cursor()
    
    with open('docs/database_schema.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
        
    for statement in sql_script.split(';'):
        if statement.strip():
            cursor.execute(statement)
            
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", ('admin', hashed, 'admin'))
        
    cursor.execute("SELECT COUNT(*) FROM rooms")
    if cursor.fetchone()[0] == 0:
        room_types = [
            ("Tiêu chuẩn", 8, 350000),
            ("Thoải mái", 8, 500000),
            ("Deluxe", 8, 700000),
            ("Suite", 4, 1200000),
            ("VIP", 2, 1800000),
            ("Gia đình", 2, 900000)
        ]
        
        room_num = 1
        for rt_name, rt_count, rt_price in room_types:
            for _ in range(rt_count):
                cursor.execute(
                    "INSERT INTO rooms (room_number, room_type, price, status) VALUES (%s, %s, %s, %s)", 
                    (f"P{room_num:03d}", rt_name, rt_price, "Trống")
                )
                room_num += 1
                
    conn.commit()
    cursor.close()
    print("Khởi tạo dữ liệu mẫu thành công! Tài khoản: admin | Mật khẩu: admin")

if __name__ == "__main__":
    seed()
