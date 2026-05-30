import datetime
import math

class BillingController:
    def __init__(self):
        self.weekend_surcharge = 0.30

    def calculate_total(self, base_price, check_in_dt, check_out_dt):
        total_price = 0
        
        current_date = check_in_dt.date()
        end_date = check_out_dt.date()
        
        nights = (end_date - current_date).days
        if nights < 1:
            nights = 1
            
        for i in range(nights):
            night_date = current_date + datetime.timedelta(days=i)
            daily_price = base_price
            if night_date.weekday() in [4, 5]:
                daily_price += base_price * self.weekend_surcharge
            total_price += daily_price
            
        base_ci = datetime.datetime.combine(check_in_dt.date(), datetime.time(14, 0))
        if check_in_dt < base_ci:
            diff_hours = (base_ci - check_in_dt).total_seconds() / 3600.0
            if diff_hours <= 4:
                total_price += (base_price / 24) * math.ceil(diff_hours)
            else:
                total_price += base_price
                
        base_co = datetime.datetime.combine(check_out_dt.date(), datetime.time(12, 0))
        if check_out_dt > base_co:
            diff_hours = (check_out_dt - base_co).total_seconds() / 3600.0
            if diff_hours <= 4:
                total_price += (base_price / 24) * math.ceil(diff_hours)
            else:
                total_price += base_price
                
        return total_price
