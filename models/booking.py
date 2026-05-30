class Booking:
    def __init__(self, booking_id=None, customer_id=None, room_id=None, check_in_date=None, check_out_date=None, total_price=None, status=None):
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.room_id = room_id
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.total_price = total_price
        self.status = status
