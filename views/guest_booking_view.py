import customtkinter as ctk
import re
import math
from datetime import datetime, timedelta
from controllers.booking_controller import BookingController
from controllers.billing_controller import BillingController
from tkcalendar import Calendar

def normalize_date_str(val):
    val = val.strip().replace("/", "-")
    if len(val) == 8 and val.isdigit():
        return f"{val[:2]}-{val[2:4]}-{val[4:]}"
    return val

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
        super().__init__(master, fg_color="#0F0F12")
        self.master = master
        self.booking_controller = BookingController()
        self.billing_controller = BillingController()
        
        # Header Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="#18181C", corner_radius=0, height=60)
        self.header_frame.pack(fill="x", side="top")

        self.back_btn = ctk.CTkButton(self.header_frame, text="🚪 QUAY LẠI", width=120, height=36, font=("Inter", 13, "bold"), fg_color="#27272A", hover_color="#3F3F46", corner_radius=6, command=self.go_back)
        self.back_btn.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.header_frame, text="🏨 HỆ THỐNG ĐẶT PHÒNG KHÁCH SẠN TRỰC TUYẾN", font=("Inter", 20, "bold"), text_color="#F8FAFC")
        self.title_label.pack(side="left", expand=True)

        # Search Container
        self.search_container = ctk.CTkFrame(self, fg_color="#18181C", corner_radius=12, border_width=1, border_color="#27272A")
        self.search_container.pack(fill="x", padx=25, pady=(15, 10))
        
        hours = [f"{i:02d}" for i in range(24)]
        minutes = ["00", "15", "30", "45"]
        
        # Row 1: Check-in & Check-out
        row1_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        row1_frame.pack(fill="x", padx=15, pady=(12, 6))
        
        ci_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        ci_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(ci_frame, text="📅 Nhận phòng:", font=("Inter", 12, "bold"), text_color="#94A3B8").pack(side="left", padx=(0, 6))
        self.check_in_entry = ctk.CTkEntry(ci_frame, placeholder_text="DD-MM-YYYY", width=120, fg_color="#0F172A", border_color="#1E293B")
        self.check_in_entry.pack(side="left", padx=3)
        self.check_in_entry.bind("<FocusOut>", lambda e: self._format_entry_date(self.check_in_entry))
        
        self.ci_btn = ctk.CTkButton(ci_frame, text="📅", width=36, fg_color="#1E293B", hover_color="#334155", command=lambda: DatePicker(self, lambda d: [self.check_in_entry.delete(0, "end"), self.check_in_entry.insert(0, d)]))
        self.ci_btn.pack(side="left", padx=3)
        
        self.ci_hour = ctk.CTkOptionMenu(ci_frame, values=hours, width=65, fg_color="#0F172A", button_color="#1E293B")
        self.ci_hour.set("14")
        self.ci_hour.pack(side="left", padx=3)
        
        self.ci_minute = ctk.CTkOptionMenu(ci_frame, values=minutes, width=65, fg_color="#0F172A", button_color="#1E293B")
        self.ci_minute.set("00")
        self.ci_minute.pack(side="left", padx=3)

        co_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        co_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(co_frame, text="📅 Trả phòng:", font=("Inter", 12, "bold"), text_color="#94A3B8").pack(side="left", padx=(0, 6))
        self.check_out_entry = ctk.CTkEntry(co_frame, placeholder_text="DD-MM-YYYY", width=120, fg_color="#0F172A", border_color="#1E293B")
        self.check_out_entry.pack(side="left", padx=3)
        self.check_out_entry.bind("<FocusOut>", lambda e: self._format_entry_date(self.check_out_entry))
        
        self.co_btn = ctk.CTkButton(co_frame, text="📅", width=36, fg_color="#1E293B", hover_color="#334155", command=lambda: DatePicker(self, lambda d: [self.check_out_entry.delete(0, "end"), self.check_out_entry.insert(0, d)]))
        self.co_btn.pack(side="left", padx=3)
        
        self.co_hour = ctk.CTkOptionMenu(co_frame, values=hours, width=65, fg_color="#0F172A", button_color="#1E293B")
        self.co_hour.set("12")
        self.co_hour.pack(side="left", padx=3)
        
        self.co_minute = ctk.CTkOptionMenu(co_frame, values=minutes, width=65, fg_color="#0F172A", button_color="#1E293B")
        self.co_minute.set("00")
        self.co_minute.pack(side="left", padx=3)

        # Row 2: Filters & Search Button
        row2_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        row2_frame.pack(fill="x", padx=15, pady=(4, 12))

        ctk.CTkLabel(row2_frame, text="Hạng phòng:", font=("Inter", 12, "bold"), text_color="#CCCCCC").pack(side="left", padx=(5, 5))
        room_types = ["Tất cả", "Tiêu chuẩn", "Thoải mái", "Deluxe", "Suite", "VIP", "Gia đình"]
        self.room_type_menu = ctk.CTkOptionMenu(row2_frame, values=room_types, width=130, fg_color="#0F172A", button_color="#1E293B")
        self.room_type_menu.set("Tất cả")
        self.room_type_menu.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(row2_frame, text="Sắp xếp giá:", font=("Inter", 12, "bold"), text_color="#CCCCCC").pack(side="left", padx=(0, 5))
        sort_options = ["Giá: Cao -> Thấp", "Giá: Thấp -> Cao"]
        self.sort_menu = ctk.CTkOptionMenu(row2_frame, values=sort_options, width=150, fg_color="#0F172A", button_color="#1E293B")
        self.sort_menu.set("Giá: Cao -> Thấp")
        self.sort_menu.pack(side="left", padx=(0, 20))

        self.search_btn = ctk.CTkButton(row2_frame, text="🔍 TÌM PHÒNG TRỐNG", font=("Inter", 13, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", width=160, height=36, corner_radius=6, command=self.search_rooms)
        self.search_btn.pack(side="right", padx=5)
        
        self.error_label = ctk.CTkLabel(self, text="", text_color="#EF4444", font=("Inter", 12))
        self.error_label.pack(pady=(0, 5))

        # Main Rooms Scrollable Display Area
        self.rooms_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.rooms_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        self.check_in_entry.insert(0, today.strftime("%d-%m-%Y"))
        self.check_out_entry.insert(0, tomorrow.strftime("%d-%m-%Y"))
        self.ci_hour.set("14")
        self.ci_minute.set("00")
        self.co_hour.set("12")
        self.co_minute.set("00")

        self.search_rooms()

    def _format_entry_date(self, entry_widget):
        raw = entry_widget.get()
        norm = normalize_date_str(raw)
        if norm != raw:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, norm)

    def search_rooms(self):
        check_in = normalize_date_str(self.check_in_entry.get())
        check_out = normalize_date_str(self.check_out_entry.get())
        
        self.check_in_entry.delete(0, "end")
        self.check_in_entry.insert(0, check_in)
        self.check_out_entry.delete(0, "end")
        self.check_out_entry.insert(0, check_out)
        
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", check_in) or not re.match(r"^\d{2}-\d{2}-\d{4}$", check_out):
            self.error_label.configure(text="Vui lòng chọn đúng định dạng ngày (VD: 20-07-2026 hoặc 20072026)")
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
        
        room_type = self.room_type_menu.get()
        sort_choice = self.sort_menu.get()
        sort_order = "DESC" if "Cao -> Thấp" in sort_choice else "ASC"
        
        self.booking_controller.find_available_rooms(
            ci_str, co_str, self.display_rooms,
            room_type=room_type, sort_order=sort_order
        )

    def display_rooms(self, rooms):
        self.after(0, self._render_rooms, rooms)

    def _render_rooms(self, rooms):
        if not rooms:
            no_room_box = ctk.CTkFrame(self.rooms_frame, fg_color="#18181C", corner_radius=10)
            no_room_box.pack(fill="x", pady=20, padx=10)
            ctk.CTkLabel(no_room_box, text="😔 Rất tiếc, không tìm thấy phòng trống phù hợp cho khoảng thời gian này.", font=("Inter", 15), text_color="#94A3B8").pack(pady=30)
            return

        try:
            ci_str = f"{self.check_in_entry.get().strip()} {self.ci_hour.get()}:{self.ci_minute.get()}:00"
            co_str = f"{self.check_out_entry.get().strip()} {self.co_hour.get()}:{self.co_minute.get()}:00"
            ci_dt = datetime.strptime(ci_str, "%d-%m-%Y %H:%M:%S")
            co_dt = datetime.strptime(co_str, "%d-%m-%Y %H:%M:%S")

            if ci_dt.date() == co_dt.date():
                diff_h = math.ceil((co_dt - ci_dt).total_seconds() / 3600.0)
                duration_text = f"{max(1, int(diff_h))} tiếng"
            else:
                nights = (co_dt.date() - ci_dt.date()).days
                base_ci = datetime.combine(ci_dt.date(), datetime.min.time()).replace(hour=14, minute=0)
                base_co = datetime.combine(co_dt.date(), datetime.min.time()).replace(hour=12, minute=0)
                
                extra_hours = 0
                if ci_dt < base_ci:
                    extra_hours += math.ceil((base_ci - ci_dt).total_seconds() / 3600.0)
                if co_dt > base_co:
                    extra_hours += math.ceil((co_dt - base_co).total_seconds() / 3600.0)
                    
                if extra_hours > 0:
                    duration_text = f"{nights} đêm {int(extra_hours)} tiếng"
                else:
                    duration_text = f"{nights} đêm"
        except Exception:
            return

        processed_rooms = []
        for room in rooms:
            base_price = float(room['price'])
            total_price = self.billing_controller.calculate_total(base_price, ci_dt, co_dt)
            processed_rooms.append((room, total_price))

        sort_choice = self.sort_menu.get()
        if "Cao -> Thấp" in sort_choice:
            processed_rooms.sort(key=lambda x: x[1], reverse=True)
        else:
            processed_rooms.sort(key=lambda x: x[1], reverse=False)

        for room, total_price in processed_rooms:
            room_card = ctk.CTkFrame(self.rooms_frame, fg_color="#18181C", corner_radius=10, border_width=1, border_color="#27272A")
            room_card.pack(fill="x", pady=6, padx=5)
            
            # Left Info
            left_info = ctk.CTkFrame(room_card, fg_color="transparent")
            left_info.pack(side="left", padx=15, pady=12)

            r_num_lbl = ctk.CTkLabel(left_info, text=f"Phòng {room['room_number']}", font=("Inter", 18, "bold"), text_color="#F8FAFC")
            r_num_lbl.pack(anchor="w")

            tag_frame = ctk.CTkFrame(left_info, fg_color="transparent")
            tag_frame.pack(anchor="w", pady=(4, 0))

            t_badge = ctk.CTkFrame(tag_frame, fg_color="#0F172A", corner_radius=10, border_width=1, border_color="#1E293B")
            t_badge.pack(side="left", padx=(0, 6))
            ctk.CTkLabel(t_badge, text=f"Hạng: {room['room_type']}", font=("Inter", 11, "bold"), text_color="#38BDF8").pack(padx=8, pady=2)

            # Features Badges
            feats = ["✨ Wifi 5G", "❄️ Điều hòa", "🛁 PT riêng"]
            for f in feats:
                fb = ctk.CTkFrame(tag_frame, fg_color="#1E1E2E", corner_radius=10)
                fb.pack(side="left", padx=3)
                ctk.CTkLabel(fb, text=f, font=("Inter", 10), text_color="#94A3B8").pack(padx=6, pady=2)

            # Right Price & Action
            right_info = ctk.CTkFrame(room_card, fg_color="transparent")
            right_info.pack(side="right", padx=15, pady=12)

            price_lbl = ctk.CTkLabel(right_info, text=f"{total_price:,.0f} VNĐ", font=("Inter", 18, "bold"), text_color="#10B981")
            price_lbl.pack(anchor="e")

            dur_lbl = ctk.CTkLabel(right_info, text=f"Tổng chi phí ({duration_text})", font=("Inter", 11), text_color="#64748B")
            dur_lbl.pack(anchor="e", pady=(0, 6))

            btn = ctk.CTkButton(right_info, text="🗝️ CHỌN ĐẶT PHÒNG", font=("Inter", 13, "bold"), fg_color="#10B981", hover_color="#059669", height=36, corner_radius=6, command=lambda r=room: self.open_booking_form(r))
            btn.pack(anchor="e")

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
