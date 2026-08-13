import datetime
import calendar
from utils.db_helper import DatabaseHelper
from controllers.billing_controller import BillingController

class ReportController:
    def __init__(self):
        self.db = DatabaseHelper()
        self.billing = BillingController()

    def get_report_data(self, period):
        # 1. Real-time Room Status & Details at NOW()
        room_stats = {"Trống": 0, "Đã book": 0, "Đã check in": 0, "Đã check out": 0, "Đang vệ sinh": 0, "Bảo trì": 0}
        room_lists = {"Trống": [], "Đã book": [], "Đã check in": [], "Đã check out": [], "Đang vệ sinh": [], "Bảo trì": []}
        room_type_stats = {}

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT r.room_id, r.room_number, r.room_type,
                       b.status as booking_status, c.first_name, c.last_name
                FROM rooms r
                LEFT JOIN bookings b ON r.room_id = b.room_id 
                     AND b.status NOT IN ('CANCELLED', 'COMPLETED')
                     AND (
                         b.status IN ('CHECKED_IN', 'CHECKED_OUT', 'CLEANING', 'MAINTENANCE')
                         OR (b.status IN ('PENDING', 'CONFIRMED') AND DATE(b.check_in_date) <= DATE(NOW()) AND DATE(b.check_out_date) >= DATE(NOW()))
                     )
                LEFT JOIN customers c ON b.customer_id = c.customer_id
                ORDER BY r.room_number ASC
            """)
            current_rooms = cursor.fetchall()
            
            processed_rooms = set()
            for r in current_rooms:
                rid = r['room_id']
                if rid in processed_rooms:
                    continue
                processed_rooms.add(rid)
                
                r_num = r['room_number']
                r_type = r['room_type'] or "Khác"
                if r_type not in room_type_stats:
                    room_type_stats[r_type] = {"total": 0, "available": 0}
                room_type_stats[r_type]["total"] += 1

                b_st = r.get('booking_status')
                c_name = f" ({r['first_name']} {r['last_name']})" if r.get('first_name') else ""

                if not b_st:
                    room_stats["Trống"] += 1
                    room_lists["Trống"].append(r_num)
                    room_type_stats[r_type]["available"] += 1
                elif b_st == 'MAINTENANCE':
                    room_stats["Bảo trì"] += 1
                    room_lists["Bảo trì"].append(r_num)
                elif b_st == 'CHECKED_IN':
                    room_stats["Đã check in"] += 1
                    room_lists["Đã check in"].append(f"{r_num}{c_name}")
                elif b_st == 'CHECKED_OUT':
                    room_stats["Đã check out"] += 1
                    room_lists["Đã check out"].append(r_num)
                elif b_st == 'CLEANING':
                    room_stats["Đang vệ sinh"] += 1
                    room_lists["Đang vệ sinh"].append(r_num)
                elif b_st in ('PENDING', 'CONFIRMED'):
                    room_stats["Đã book"] += 1
                    room_lists["Đã book"].append(f"{r_num}{c_name}")
                else:
                    room_stats["Trống"] += 1
                    room_lists["Trống"].append(r_num)
                    room_type_stats[r_type]["available"] += 1
        except Exception as e:
            print("Pie Chart DB Error:", e)

        # 2. Revenue Bar Chart Data
        labels = []
        revenue_data = []
        chart_title = ""

        try:
            query = """
                SELECT b.status, b.check_in_date, b.check_out_date, b.actual_check_out_time, r.price 
                FROM bookings b
                JOIN rooms r ON b.room_id = r.room_id
                WHERE b.status NOT IN ('CANCELLED', 'MAINTENANCE')
            """
            cursor.execute(query)
            bookings = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print("Revenue DB Error:", e)
            bookings = []

        now = datetime.datetime.now()
        today = now.date()

        if period == 'day':
            year = today.year
            month = today.month
            last_day = calendar.monthrange(year, month)[1]
            days_count = today.day # Show days in current month up to today

            labels = [f"{d:02d}/{month:02d}" for d in range(1, days_count + 1)]
            revenue_data = [0.0] * days_count
            chart_title = f"Doanh thu từng ngày (Tháng {month:02d}/{year})"

            for b in bookings:
                ci = b['check_in_date']
                co = b['check_out_date']
                eff_co_date = b['actual_check_out_time'].date() if b['actual_check_out_time'] else co.date()
                val = self.billing.calculate_total(float(b['price']), ci, co)
                
                if eff_co_date.year == year and eff_co_date.month == month and 1 <= eff_co_date.day <= days_count:
                    revenue_data[eff_co_date.day - 1] += val

        elif period == 'week':
            year = today.year
            month = today.month
            last_day = calendar.monthrange(year, month)[1]

            week_ranges = [
                (1, 7, f"Tuần 1\n(01-07/{month:02d})"),
                (8, 14, f"Tuần 2\n(08-14/{month:02d})"),
                (15, 21, f"Tuần 3\n(15-21/{month:02d})"),
                (22, 28, f"Tuần 4\n(22-28/{month:02d})"),
            ]
            if last_day > 28:
                week_ranges.append((29, last_day, f"Tuần 5\n(29-{last_day:02d}/{month:02d})"))

            labels = [w[2] for w in week_ranges]
            revenue_data = [0.0] * len(week_ranges)
            chart_title = f"Doanh thu theo tuần (Tháng {month:02d}/{year})"

            for b in bookings:
                ci = b['check_in_date']
                co = b['check_out_date']
                eff_co_date = b['actual_check_out_time'].date() if b['actual_check_out_time'] else co.date()
                val = self.billing.calculate_total(float(b['price']), ci, co)

                if eff_co_date.year == year and eff_co_date.month == month:
                    day_num = eff_co_date.day
                    for idx, (w_start, w_end, _) in enumerate(week_ranges):
                        if w_start <= day_num <= w_end:
                            revenue_data[idx] += val
                            break

        elif period == 'month':
            labels = []
            revenue_data = [0.0] * 6
            month_tuples = []
            
            for i in range(5, -1, -1):
                m = (today.month - i - 1) % 12 + 1
                y = today.year + ((today.month - i - 1) // 12)
                labels.append(f"Tháng {m:02d}/{y}")
                month_tuples.append((y, m))

            chart_title = "Doanh thu 6 tháng gần nhất"

            for b in bookings:
                ci = b['check_in_date']
                co = b['check_out_date']
                eff_co_date = b['actual_check_out_time'].date() if b['actual_check_out_time'] else co.date()
                val = self.billing.calculate_total(float(b['price']), ci, co)

                for idx, (y, m) in enumerate(month_tuples):
                    if eff_co_date.year == y and eff_co_date.month == m:
                        revenue_data[idx] += val
                        break

        return labels, revenue_data, room_stats, room_lists, room_type_stats, chart_title
