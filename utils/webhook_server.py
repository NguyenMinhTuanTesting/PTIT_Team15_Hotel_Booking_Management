from flask import Flask, request
from utils.db_helper import DatabaseHelper

app = Flask(__name__)
db = DatabaseHelper()

@app.route('/api/confirm', methods=['GET'])
def confirm_booking():
    booking_id = request.args.get('id')
    if not booking_id:
        return "Missing ID", 400
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'CONFIRMED' WHERE booking_id = %s", (booking_id,))
        conn.commit()
        cursor.close()
        return "Xác nhận đặt phòng thành công", 200
    except Exception:
        return "Lỗi hệ thống", 500

@app.route('/api/reject', methods=['GET'])
def reject_booking():
    booking_id = request.args.get('id')
    if not booking_id:
        return "Missing ID", 400
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'CANCELLED' WHERE booking_id = %s", (booking_id,))
        conn.commit()
        cursor.close()
        return "Hủy đặt phòng thành công", 200
    except Exception:
        return "Lỗi hệ thống", 500

def start_server():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='127.0.0.1', port=5000, use_reloader=False)
