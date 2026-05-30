import time
import threading
from utils.db_helper import DatabaseHelper

class BookingScheduler:
    def __init__(self):
        self.db = DatabaseHelper()
        
    def start(self):
        threading.Thread(target=self._run, daemon=True).start()
        
    def _run(self):
        while True:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                query = "UPDATE bookings SET status = 'CANCELLED' WHERE status = 'PENDING' AND TIMESTAMPDIFF(MINUTE, created_at, NOW()) > 15"
                cursor.execute(query)
                conn.commit()
                cursor.close()
            except Exception:
                pass
            time.sleep(60)
