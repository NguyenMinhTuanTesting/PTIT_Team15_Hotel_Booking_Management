import datetime
from utils.db_helper import DatabaseHelper
from controllers.billing_controller import BillingController

class ReportController:
    def __init__(self):
        self.db = DatabaseHelper()
        self.billing = BillingController()

    def get_report_data(self, period):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Fetch all revenue-generating bookings
            query = """
                SELECT b.status, b.check_in_date, b.check_out_date, b.actual_check_out_time, r.price, r.room_type 
                FROM bookings b
                JOIN rooms r ON b.room_id = r.room_id
                WHERE b.status NOT IN ('CANCELLED', 'MAINTENANCE')
            """
            cursor.execute(query)
            bookings = cursor.fetchall()
            
            # Calculate period boundaries for Pie Chart
            today_dt = datetime.datetime.now()
            if period == 'day':
                p_start = today_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                p_end = today_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif period == 'week':
                p_start = (today_dt - datetime.timedelta(days=today_dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
                p_end = (p_start + datetime.timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
            else: # month
                p_start = today_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                import calendar
                last_day = calendar.monthrange(today_dt.year, today_dt.month)[1]
                p_end = today_dt.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Fetch room status for the selected period (prioritizing active statuses)
            cursor.execute("""
                SELECT r.room_id, b.status as booking_status 
                FROM rooms r
                LEFT JOIN bookings b ON r.room_id = b.room_id 
                     AND b.status NOT IN ('CANCELLED', 'COMPLETED')
                     AND (
                         (b.status IN ('PENDING', 'CONFIRMED', 'MAINTENANCE') AND b.check_in_date <= %s AND b.check_out_date >= %s)
                         OR (b.status = 'CHECKED_IN')
                         OR (b.status = 'CHECKED_OUT')
                         OR (b.status = 'CLEANING' AND DATE_ADD(b.cleaning_start_time, INTERVAL 30 MINUTE) >= NOW())
                     )
                ORDER BY r.room_id, 
                    CASE b.status 
                        WHEN 'CHECKED_IN' THEN 1 
                        WHEN 'CHECKED_OUT' THEN 2 
                        WHEN 'CLEANING' THEN 3
                        WHEN 'MAINTENANCE' THEN 4
                        WHEN 'CONFIRMED' THEN 5 
                        WHEN 'PENDING' THEN 6
                        ELSE 7 
                    END
            """, (p_end, p_start))
            current_rooms = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print("DB Error:", e)
            return [], [], {"Trống": 32, "Bảo trì": 0, "Đã check in": 0, "Đã book": 0, "Đã check out": 0}

        # Calculate room stats pie chart
        room_stats = {"Trống": 0, "Đã book": 0, "Đã check in": 0, "Đã check out": 0, "Đang vệ sinh": 0, "Bảo trì": 0}
        processed_rooms = set()
        for r in current_rooms:
            rid = r['room_id']
            if rid in processed_rooms:
                continue
            processed_rooms.add(rid)
            
            b_st = r.get('booking_status')
            if not b_st:
                room_stats["Trống"] += 1
            elif b_st == 'MAINTENANCE':
                room_stats["Bảo trì"] += 1
            elif b_st == 'CHECKED_IN':
                room_stats["Đã check in"] += 1
            elif b_st == 'CHECKED_OUT':
                room_stats["Đã check out"] += 1
            elif b_st == 'CLEANING':
                room_stats["Đang vệ sinh"] += 1
            elif b_st in ('PENDING', 'CONFIRMED'):
                room_stats["Đã book"] += 1
            else:
                room_stats["Trống"] += 1

        today = datetime.datetime.now().date()
        labels = []
        revenue_data = []

        if period == 'day':
            labels = [(today - datetime.timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)]
            revenue_data = [0] * 7
            for b in bookings:
                ci = b['check_in_date']
                co = b['check_out_date']
                # If they checked out early, count revenue on the actual checkout date
                eff_co_date = b['actual_check_out_time'].date() if b['actual_check_out_time'] else co.date()
                val = self.billing.calculate_total(float(b['price']), ci, co)
                
                if today - datetime.timedelta(days=6) <= eff_co_date <= today:
                    idx = 6 - (today - eff_co_date).days
                    revenue_data[idx] += val

        elif period == 'week':
            labels = [f"Tuần {i+1}" for i in range(4)]
            revenue_data = [0] * 4
            start_date = today - datetime.timedelta(days=28)
            for b in bookings:
                ci = b['check_in_date']
                co = b['check_out_date']
                eff_co_date = b['actual_check_out_time'].date() if b['actual_check_out_time'] else co.date()
                val = self.billing.calculate_total(float(b['price']), ci, co)
                
                if start_date < eff_co_date <= today:
                    days_diff = (today - eff_co_date).days
                    week_idx = 3 - (days_diff // 7)
                    if 0 <= week_idx < 4:
                        revenue_data[week_idx] += val

        elif period == 'month':
            labels = []
            revenue_data = [0] * 6
            for i in range(5, -1, -1):
                m = (today.month - i - 1) % 12 + 1
                y = today.year + ((today.month - i - 1) // 12)
                labels.append(f"{m}/{y}")
                
            for b in bookings:
                ci = b['check_in_date']
                co = b['check_out_date']
                eff_co_date = b['actual_check_out_time'].date() if b['actual_check_out_time'] else co.date()
                val = self.billing.calculate_total(float(b['price']), ci, co)
                
                for i in range(6):
                    m = (today.month - (5-i) - 1) % 12 + 1
                    y = today.year + ((today.month - (5-i) - 1) // 12)
                    if eff_co_date.year == y and eff_co_date.month == m:
                        revenue_data[i] += val
                        break

        return labels, revenue_data, room_stats
