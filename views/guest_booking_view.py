import customtkinter as ctk
import re
from datetime import datetime
from controllers.booking_controller import BookingController
from controllers.billing_controller import BillingController
from tkcalendar import Calendar

class DatePicker(ctk.CTkToplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Chọn ngày")
        self.geometry("300x300")
        self.attributes("-topmost", True)
        self.grab_set()
        
        self.cal = Calendar(self, selectmode='day', date_pattern='dd-mm-yyyy')
        self.cal.pack(pady=20, fill="both", expand=True)
        
        btn = ctk.CTkButton(self, text="Chọn", command=lambda: self.select(callback))
        btn.pack(pady=10)
        
    def select(self, callback):
        selected_date = self.cal.get_date()
        callback(selected_date)
        self.destroy()

class GuestBookingView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#121212")
        self.master = master
        self.booking_controller = BookingController()
        self.billing_controller = BillingController()
        
        self.back_btn = ctk.CTkButton(self, text="QUAY LẠI", width=120, height=40, font=("Inter", 14, "bold"), fg_color="transparent", border_width=1, border_color="#333333", hover_color="#1E1E1E", command=self.go_back)
        self.back_btn.place(relx=0.05, rely=0.05)

        self.title_label = ctk.CTkLabel(self, text="ĐẶT PHÒNG KHÁCH SẠN", font=("Inter", 28, "bold"), text_color="#FFFFFF")
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")

        self.search_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        self.search_frame.place(relx=0.5, rely=0.25, anchor="center", relwidth=0.85)
        
        hours = [f"{i:02d}" for i in range(24)]
        minutes = ["00", "15", "30", "45"]
        
        # Check-in Row
        ci_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        ci_frame.pack(side="left", padx=10, pady=20)
        
        self.check_in_entry = ctk.CTkEntry(ci_frame, placeholder_text="Check-in (DD-MM-YYYY)", width=140)
        self.check_in_entry.pack(side="left", padx=5)
        
        self.ci_btn = ctk.CTkButton(ci_frame, text="📅", width=40, command=lambda: DatePicker(self, lambda d: [self.check_in_entry.delete(0, "end"), self.check_in_entry.insert(0, d)]))
        self.ci_btn.pack(side="left", padx=5)
        
        self.ci_hour = ctk.CTkOptionMenu(ci_frame, values=hours, width=70)
        self.ci_hour.set("14")
        self.ci_hour.pack(side="left", padx=5)
        
        self.ci_minute = ctk.CTkOptionMenu(ci_frame, values=minutes, width=70)
        self.ci_minute.set("00")
        self.ci_minute.pack(side="left", padx=5)

        # Check-out Row
        co_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        co_frame.pack(side="left", padx=10, pady=20)
        
        self.check_out_entry = ctk.CTkEntry(co_frame, placeholder_text="Check-out (DD-MM-YYYY)", width=140)
        self.check_out_entry.pack(side="left", padx=5)
        
        self.co_btn = ctk.CTkButton(co_frame, text="📅", width=40, command=lambda: DatePicker(self, lambda d: [self.check_out_entry.delete(0, "end"), self.check_out_entry.insert(0, d)]))
        self.co_btn.pack(side="left", padx=5)
        
        self.co_hour = ctk.CTkOptionMenu(co_frame, values=hours, width=70)
        self.co_hour.set("12")
        self.co_hour.pack(side="left", padx=5)
        
        self.co_minute = ctk.CTkOptionMenu(co_frame, values=minutes, width=70)
        self.co_minute.set("00")
        self.co_minute.pack(side="left", padx=5)

        self.search_btn = ctk.CTkButton(self.search_frame, text="TÌM PHÒNG", font=("Inter", 14, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", command=self.search_rooms)
        self.search_btn.pack(side="right", padx=20, pady=20)
        
        self.error_label = ctk.CTkLabel(self, text="", text_color="#EF4444", font=("Inter", 12))
        self.error_label.place(relx=0.5, rely=0.35, anchor="center")

        self.rooms_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.rooms_frame.place(relx=0.5, rely=0.67, anchor="center", relwidth=0.85, relheight=0.5)

    def search_rooms(self):
        check_in = self.check_in_entry.get().strip()
        check_out = self.check_out_entry.get().strip()
        
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", check_in) or not re.match(r"^\d{2}-\d{2}-\d{4}$", check_out):
            self.error_label.configure(text="Vui lòng chọn đúng định dạng ngày (VD: 27-05-2026)")
            return
            
        try:
            ci_date = datetime.strptime(f"{check_in} {self.ci_hour.get()}:{self.ci_minute.get()}:00", "%d-%m-%Y %H:%M:%S")
            co_date = datetime.strptime(f"{check_out} {self.co_hour.get()}:{self.co_minute.get()}:00", "%d-%m-%Y %H:%M:%S")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if ci_date.date() < today.date():
                self.error_label.configure(text="Ngày Check-in không được trong quá khứ")
                return
            if ci_date >= co_date:
                self.error_label.configure(text="Thời gian Check-out phải sau Check-in")
                return
        except ValueError:
            self.error_label.configure(text="Thời gian không hợp lệ")
            return

        self.error_label.configure(text="")
        for widget in self.rooms_frame.winfo_children():
            widget.destroy()
            
        ci_str = ci_date.strftime("%Y-%m-%d %H:%M:%S")
        co_str = co_date.strftime("%Y-%m-%d %H:%M:%S")
        self.booking_controller.find_available_rooms(ci_str, co_str, self.display_rooms)

    def display_rooms(self, rooms):
        self.after(0, self._render_rooms, rooms)

    def _render_rooms(self, rooms):
        if not rooms:
            ctk.CTkLabel(self.rooms_frame, text="Không có phòng trống phù hợp.", font=("Inter", 16)).pack(pady=20)
            return

        try:
            ci_str = f"{self.check_in_entry.get().strip()} {self.ci_hour.get()}:{self.ci_minute.get()}:00"
            co_str = f"{self.check_out_entry.get().strip()} {self.co_hour.get()}:{self.co_minute.get()}:00"
            ci_dt = datetime.strptime(ci_str, "%d-%m-%Y %H:%M:%S")
            co_dt = datetime.strptime(co_str, "%d-%m-%Y %H:%M:%S")
            nights = max(1, (co_dt.date() - ci_dt.date()).days)
        except Exception:
            return

        for room in rooms:
            room_frame = ctk.CTkFrame(self.rooms_frame, fg_color="#27272A", corner_radius=8)
            room_frame.pack(fill="x", pady=5, padx=10)
            
            base_price = float(room['price'])
            total_price = self.billing_controller.calculate_total(base_price, ci_dt, co_dt)
            
            info_text = f"Phòng {room['room_number']} - Hạng: {room['room_type']} | Tổng tiền: {total_price:,.0f} VNĐ ({nights} đêm)"
            
            ctk.CTkLabel(room_frame, text=info_text, font=("Inter", 16, "bold")).pack(side="left", padx=20, pady=15)
            ctk.CTkButton(room_frame, text="CHỌN PHÒNG", fg_color="#10B981", hover_color="#059669", command=lambda r=room: self.open_booking_form(r)).pack(side="right", padx=20, pady=15)

    def open_booking_form(self, room_data):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Đặt phòng {room_data['room_number']}")
        popup.geometry("400x550")
        popup.attributes("-topmost", True)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Thông tin khách hàng", font=("Inter", 20, "bold")).pack(pady=20)

        entries = {}
        fields = [("first_name", "Họ"), ("last_name", "Tên"), ("phone", "Số điện thoại"), ("email", "Email")]
        
        for key, placeholder in fields:
            entry = ctk.CTkEntry(popup, placeholder_text=placeholder, width=300, height=40)
            entry.pack(pady=10)
            entries[key] = entry
            
        error_lbl = ctk.CTkLabel(popup, text="", text_color="#EF4444", font=("Inter", 12))
        error_lbl.pack(pady=5)

        def submit():
            fn = entries["first_name"].get().strip()
            ln = entries["last_name"].get().strip()
            ph = entries["phone"].get().strip()
            em = entries["email"].get().strip()
            
            if not fn or not ln or not ph or not em:
                error_lbl.configure(text="Vui lòng điền đầy đủ thông tin")
                return
            if not re.match(r"^\d{10,11}$", ph):
                error_lbl.configure(text="Số điện thoại không hợp lệ")
                return
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", em):
                error_lbl.configure(text="Email không hợp lệ")
                return
                
            error_lbl.configure(text="Đang xử lý...", text_color="#F59E0B")
            
            ci_str = datetime.strptime(f"{self.check_in_entry.get().strip()} {self.ci_hour.get()}:{self.ci_minute.get()}:00", "%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            co_str = datetime.strptime(f"{self.check_out_entry.get().strip()} {self.co_hour.get()}:{self.co_minute.get()}:00", "%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            
            self.booking_controller.create_booking(
                fn, ln, ph, em, room_data["room_id"], 
                ci_str, co_str, 
                lambda success: self.after(0, self.on_booking_complete, success, popup)
            )
            
        ctk.CTkButton(popup, text="ĐẶT PHÒNG", width=300, height=45, font=("Inter", 16, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", command=submit).pack(pady=20)

    def on_booking_complete(self, success, popup):
        if success:
            popup.destroy()
            success_popup = ctk.CTkToplevel(self)
            success_popup.title("Thành công")
            success_popup.geometry("300x150")
            success_popup.attributes("-topmost", True)
            ctk.CTkLabel(success_popup, text="Đặt phòng thành công!\nVui lòng kiểm tra email.", font=("Inter", 14), text_color="#10B981").pack(pady=30)
            ctk.CTkButton(success_popup, text="ĐÓNG", command=lambda: [success_popup.destroy(), self.search_rooms()]).pack()
        else:
            for widget in popup.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and widget.cget("text_color") == "#F59E0B":
                    widget.configure(text="Lỗi hệ thống, vui lòng thử lại", text_color="#EF4444")

    def go_back(self):
        from views.welcome_view import WelcomeView
        for widget in self.master.winfo_children():
            widget.destroy()
        welcome_view = WelcomeView(self.master)
        welcome_view.pack(fill="both", expand=True)
