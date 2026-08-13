import customtkinter as ctk
import re
from datetime import datetime
import datetime as dt_module
from controllers.room_controller import RoomController
from controllers.booking_controller import BookingController
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

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user=None):
        super().__init__(master, fg_color="#0F0F12")
        self.master = master
        self.user = user
        self.room_controller = RoomController()
        self.booking_controller = BookingController()
        
        # Header Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="#18181C", corner_radius=0, height=60)
        self.header_frame.pack(fill="x", side="top")

        self.logout_btn = ctk.CTkButton(self.header_frame, text="🚪 ĐĂNG XUẤT", width=120, height=36, font=("Inter", 13, "bold"), fg_color="#DC2626", hover_color="#B91C1C", corner_radius=6, command=self.logout)
        self.logout_btn.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.header_frame, text="📋 SƠ ĐỒ VẬN HÀNH & TRẠNG THÁI PHÒNG (NHÂN VIÊN)", font=("Inter", 20, "bold"), text_color="#F8FAFC")
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

        ctk.CTkLabel(row2_frame, text="Sắp xếp:", font=("Inter", 12, "bold"), text_color="#CCCCCC").pack(side="left", padx=(0, 5))
        sort_options = ["Mặc định (Số phòng)", "Giá: Cao -> Thấp", "Giá: Thấp -> Cao"]
        self.sort_menu = ctk.CTkOptionMenu(row2_frame, values=sort_options, width=170, fg_color="#0F172A", button_color="#1E293B")
        self.sort_menu.set("Mặc định (Số phòng)")
        self.sort_menu.pack(side="left", padx=(0, 20))

        self.search_btn = ctk.CTkButton(row2_frame, text="🔍 TÌM PHÒNG", font=("Inter", 13, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", width=140, height=36, corner_radius=6, command=self.load_rooms)
        self.search_btn.pack(side="right", padx=5)

        self.error_label = ctk.CTkLabel(self, text="", text_color="#EF4444", font=("Inter", 12))
        self.error_label.pack(pady=(0, 2))

        self.status_colors = {
            "Trống": "#10B981",
            "Đã book": "#F59E0B",
            "Đã check in": "#F43F5E",
            "Đã check out": "#818CF8",
            "Đang vệ sinh": "#3B82F6",
            "Bảo trì": "#64748B"
        }

        self.selected_status_filter = "Tất cả"
        self.cached_rooms = []

        # Interactive Status Filter Bar
        self.legend_frame = ctk.CTkFrame(self, fg_color="#18181C", corner_radius=10, border_width=1, border_color="#27272A")
        self.legend_frame.pack(fill="x", padx=25, pady=(0, 10))

        # Rooms Grid Display Area
        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))
        
        today = datetime.now()
        tomorrow = today + dt_module.timedelta(days=1)
        
        self.check_in_entry.insert(0, today.strftime("%d-%m-%Y"))
        self.check_out_entry.insert(0, tomorrow.strftime("%d-%m-%Y"))
        self.ci_hour.set("14")
        self.ci_minute.set("00")
        self.co_hour.set("12")
        self.co_minute.set("00")
        
        self.current_ci_dt = None
        self.current_co_dt = None
        self.load_rooms()

    def _format_entry_date(self, entry_widget):
        raw = entry_widget.get()
        norm = normalize_date_str(raw)
        if norm != raw:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, norm)

    def load_rooms(self):
        check_in = normalize_date_str(self.check_in_entry.get())
        check_out = normalize_date_str(self.check_out_entry.get())
        
        self.check_in_entry.delete(0, "end")
        self.check_in_entry.insert(0, check_in)
        self.check_out_entry.delete(0, "end")
        self.check_out_entry.insert(0, check_out)
        
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", check_in) or not re.match(r"^\d{2}-\d{2}-\d{4}$", check_out):
            self.error_label.configure(text="Định dạng ngày không hợp lệ (VD: 20-07-2026 hoặc 20072026)")
            return
            
        try:
            ci_date = datetime.strptime(f"{check_in} {self.ci_hour.get()}:{self.ci_minute.get()}:00", "%d-%m-%Y %H:%M:%S")
            co_date = datetime.strptime(f"{check_out} {self.co_hour.get()}:{self.co_minute.get()}:00", "%d-%m-%Y %H:%M:%S")
            if ci_date >= co_date:
                self.error_label.configure(text="Thời gian Check-out phải sau Check-in")
                return
        except ValueError:
            self.error_label.configure(text="Thời gian không hợp lệ")
            return

        self.error_label.configure(text="")
        self.current_ci_dt = ci_date
        self.current_co_dt = co_date
        
        ci_str = ci_date.strftime("%Y-%m-%d %H:%M:%S")
        co_str = co_date.strftime("%Y-%m-%d %H:%M:%S")
        
        room_type = self.room_type_menu.get()
        sort_choice = self.sort_menu.get()
        sort_order = None
        if "Cao -> Thấp" in sort_choice:
            sort_order = "DESC"
        elif "Thấp -> Cao" in sort_choice:
            sort_order = "ASC"

        self.room_controller.get_rooms_status_by_time(
            ci_str, co_str, self.on_rooms_loaded,
            room_type=room_type, sort_order=sort_order
        )

    def on_rooms_loaded(self, rooms):
        self.cached_rooms = rooms or []
        self.after(0, self.update_dashboard_view)

    def update_dashboard_view(self):
        self.render_filter_chips()
        self.render_grid(self.cached_rooms)

    def render_filter_chips(self):
        for w in self.legend_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.legend_frame, text="Bộ lọc trạng thái:", font=("Inter", 11, "bold"), text_color="#94A3B8").pack(side="left", padx=12, pady=8)

        # Count per status
        counts = {"Tất cả": len(self.cached_rooms)}
        for r in self.cached_rooms:
            st = r.get("status", "Trống")
            counts[st] = counts.get(st, 0) + 1

        filters = [("Tất cả", "#38BDF8")] + [(k, v) for k, v in self.status_colors.items()]

        for f_name, color in filters:
            cnt = counts.get(f_name, 0)
            btn_txt = f"{f_name} ({cnt})"
            is_active = (self.selected_status_filter == f_name)

            if is_active:
                btn_fg = color
                btn_txt_col = "#FFFFFF"
                btn_border = color
            else:
                btn_fg = "#0F172A"
                btn_txt_col = "#94A3B8"
                btn_border = "#1E293B"

            btn = ctk.CTkButton(
                self.legend_frame,
                text=btn_txt,
                font=("Inter", 11, "bold"),
                fg_color=btn_fg,
                text_color=btn_txt_col,
                hover_color=color,
                border_width=1,
                border_color=btn_border,
                corner_radius=12,
                height=28,
                command=lambda name=f_name: self.set_status_filter(name)
            )
            btn.pack(side="left", padx=4, pady=6)

    def set_status_filter(self, filter_name):
        self.selected_status_filter = filter_name
        self.render_filter_chips()
        self.render_grid(self.cached_rooms)

    def render_grid(self, rooms):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Apply active status filter
        if self.selected_status_filter != "Tất cả":
            filtered_rooms = [r for r in rooms if r.get("status") == self.selected_status_filter]
        else:
            filtered_rooms = rooms

        if not filtered_rooms:
            no_box = ctk.CTkFrame(self.grid_frame, fg_color="#18181C", corner_radius=10)
            no_box.pack(fill="x", pady=20, padx=10)
            ctk.CTkLabel(no_box, text=f"Không có phòng nào ở trạng thái '{self.selected_status_filter}'", font=("Inter", 14), text_color="#94A3B8").pack(pady=20)
            return

        columns = 6 # Responsive 6-column grid for desktop
        for c in range(columns):
            self.grid_frame.columnconfigure(c, weight=1)

        for i, room_data in enumerate(filtered_rooms):
            status = room_data.get("status", "Trống")
            color = self.status_colors.get(status, "#64748B")
            
            # Responsive Room Card expanding to full column width
            card = ctk.CTkFrame(self.grid_frame, fg_color="#18181C", corner_radius=10, border_width=2, border_color=color, height=115)
            card.grid(row=i // columns, column=i % columns, padx=6, pady=6, sticky="ew")
            card.grid_propagate(False)

            # Room Header (Clear gap between room number & type name)
            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.pack(fill="x", padx=10, pady=(8, 2))

            ctk.CTkLabel(hdr, text=f"P.{room_data['room_number']}", font=("Inter", 16, "bold"), text_color="#F8FAFC").pack(side="left")
            
            r_type_str = room_data.get('room_type', 'Tiêu chuẩn')
            ctk.CTkLabel(hdr, text=r_type_str, font=("Inter", 10, "bold"), text_color="#38BDF8").pack(side="right")

            # Status Badge Pill
            st_badge = ctk.CTkFrame(card, fg_color=color, corner_radius=8)
            st_badge.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(st_badge, text=status, font=("Inter", 10, "bold"), text_color="#FFFFFF").pack(pady=2)

            # Bottom Detail: Customer Name if present, else Price
            bot_frame = ctk.CTkFrame(card, fg_color="transparent")
            bot_frame.pack(fill="x", padx=10, pady=(2, 6))

            c_name = room_data.get('customer_name')
            if c_name:
                ctk.CTkLabel(bot_frame, text=f"👤 {c_name}", font=("Inter", 10, "bold"), text_color="#F1F5F9", anchor="w").pack(side="left")
            else:
                price_val = float(room_data.get('price', 0))
                ctk.CTkLabel(bot_frame, text=f"{price_val:,.0f}đ/đêm", font=("Inter", 9), text_color="#94A3B8", anchor="w").pack(side="left")

            # Bind click event on card and all children
            def make_click_cmd(r=room_data):
                return lambda e: self.open_room_popup(r)

            cmd = make_click_cmd(room_data)
            card.bind("<Button-1>", cmd)
            for child in card.winfo_children():
                child.bind("<Button-1>", cmd)
                for subchild in child.winfo_children():
                    subchild.bind("<Button-1>", cmd)

    def open_room_popup(self, room_data):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Tác vụ phòng {room_data['room_number']}")
        popup.geometry("400x500")
        popup.attributes("-topmost", True)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Phòng {room_data['room_number']} - {room_data['room_type']}", font=("Inter", 18, "bold")).pack(pady=(15, 2))
        ctk.CTkLabel(popup, text=f"Trạng thái: {room_data['status']}", font=("Inter", 14), text_color=self.status_colors.get(room_data['status'], "#FFFFFF")).pack(pady=(0, 8))
        
        # Display detailed booking information if available
        if room_data.get('booking_check_in') and room_data.get('booking_check_out'):
            info_frame = ctk.CTkFrame(popup, fg_color="#27272A", corner_radius=8)
            info_frame.pack(fill="x", padx=20, pady=5)
            
            b_ci = room_data['booking_check_in']
            b_co = room_data['booking_check_out']
            ci_fmt = b_ci.strftime("%H:%M %d-%m-%Y") if isinstance(b_ci, datetime) else str(b_ci)
            co_fmt = b_co.strftime("%H:%M %d-%m-%Y") if isinstance(b_co, datetime) else str(b_co)
            
            if room_data.get('customer_name'):
                ctk.CTkLabel(info_frame, text=f"👤 Khách: {room_data['customer_name']}", font=("Inter", 13, "bold"), text_color="#E2E8F0").pack(anchor="w", padx=12, pady=(8, 2))
            if room_data.get('customer_phone'):
                ctk.CTkLabel(info_frame, text=f"📞 SĐT: {room_data['customer_phone']}", font=("Inter", 12), text_color="#94A3B8").pack(anchor="w", padx=12, pady=2)
                
            ctk.CTkLabel(info_frame, text=f"📅 Check-in thực tế:  {ci_fmt}", font=("Inter", 12), text_color="#38BDF8").pack(anchor="w", padx=12, pady=2)
            ctk.CTkLabel(info_frame, text=f"📅 Check-out thực tế: {co_fmt}", font=("Inter", 12), text_color="#F43F5E").pack(anchor="w", padx=12, pady=(2, 8))

        ci_str = self.current_ci_dt.strftime("%Y-%m-%d %H:%M:%S")
        co_str = self.current_co_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        if room_data['status'] == 'Trống':
            ctk.CTkButton(
                popup, text="ĐẶT PHÒNG CHO KHÁCH", fg_color="#10B981", hover_color="#059669", font=("Inter", 14, "bold"), height=40,
                command=lambda: [popup.destroy(), self.open_booking_form(room_data)]
            ).pack(pady=8, padx=20, fill="x")
            
            ctk.CTkButton(
                popup, text="Đánh dấu Bảo trì", fg_color="#6B7280", hover_color="#4B5563", font=("Inter", 13), height=36,
                command=lambda: [self.room_controller.mark_maintenance(room_data['room_id'], ci_str, co_str, lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=5, padx=20, fill="x")
        elif room_data['status'] == 'Bảo trì':
            ctk.CTkButton(
                popup, text="Hủy Bảo trì", fg_color="#22C55E", hover_color="#16A34A", font=("Inter", 14, "bold"), height=40,
                command=lambda: [self.room_controller.remove_maintenance(room_data['booking_id'], lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=8, padx=20, fill="x")
        elif room_data['status'] == 'Đã book':
            ctk.CTkButton(
                popup, text="Khách Check-in", fg_color="#EF4444", hover_color="#DC2626", font=("Inter", 14, "bold"), height=40,
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CHECKED_IN', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=8, padx=20, fill="x")
            ctk.CTkButton(
                popup, text="Khách Không Tới (Hủy)", fg_color="#6B7280", hover_color="#4B5563", font=("Inter", 13), height=36,
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CANCELLED', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=5, padx=20, fill="x")
        elif room_data['status'] == 'Đã check in':
            ctk.CTkButton(
                popup, text="Khách Check-out", fg_color="#475569", hover_color="#334155", font=("Inter", 14, "bold"), height=40,
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CHECKED_OUT', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=8, padx=20, fill="x")
        elif room_data['status'] == 'Đã check out':
            ctk.CTkButton(
                popup, text="Bắt đầu vệ sinh", fg_color="#2563EB", hover_color="#1D4ED8", font=("Inter", 14, "bold"), height=40,
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CLEANING', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=8, padx=20, fill="x")
        elif room_data['status'] == 'Đang vệ sinh':
            ctk.CTkLabel(popup, text="Đang vệ sinh (Tự động sạch sau 30 phút)", font=("Inter", 12), text_color="#EAB308").pack(pady=5)
            ctk.CTkButton(
                popup, text="Hoàn tất dọn sớm", fg_color="#22C55E", hover_color="#16A34A", font=("Inter", 14, "bold"), height=40,
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'COMPLETED', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=8, padx=20, fill="x")

    def open_booking_form(self, room_data):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Đặt phòng {room_data['room_number']} cho Khách")
        popup.geometry("400x520")
        popup.attributes("-topmost", True)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"ĐẶT PHÒNG {room_data['room_number']}", font=("Inter", 20, "bold"), text_color="#FFFFFF").pack(pady=(15, 2))
        ctk.CTkLabel(popup, text=f"Hạng: {room_data['room_type']} - Giá: {float(room_data['price']):,.0f} VNĐ/đêm", font=("Inter", 13), text_color="#A1A1AA").pack(pady=(0, 10))

        entries = {}
        fields = [("first_name", "Họ khách hàng"), ("last_name", "Tên khách hàng"), ("phone", "Số điện thoại"), ("email", "Email")]
        
        for key, placeholder in fields:
            entry = ctk.CTkEntry(popup, placeholder_text=placeholder, width=320, height=40)
            entry.pack(pady=6)
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
                error_lbl.configure(text="Số điện thoại không hợp lệ (10-11 chữ số)")
                return
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", em):
                error_lbl.configure(text="Email không hợp lệ")
                return
                
            error_lbl.configure(text="Đang xử lý đặt phòng...", text_color="#F59E0B")
            
            ci_str = self.current_ci_dt.strftime("%Y-%m-%d %H:%M:%S")
            co_str = self.current_co_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            self.booking_controller.create_booking(
                fn, ln, ph, em, room_data["room_id"], 
                ci_str, co_str, 
                lambda success: self.after(0, self.on_staff_booking_complete, success, popup)
            )
            
        ctk.CTkButton(popup, text="XÁC NHẬN ĐẶT PHÒNG", width=320, height=45, font=("Inter", 16, "bold"), fg_color="#10B981", hover_color="#059669", command=submit).pack(pady=15)

    def on_staff_booking_complete(self, success, popup):
        if success:
            popup.destroy()
            self.load_rooms()
        else:
            for widget in popup.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and widget.cget("text_color") == "#F59E0B":
                    widget.configure(text="Lỗi hệ thống, vui lòng thử lại", text_color="#EF4444")

    def logout(self):
        from views.welcome_view import WelcomeView
        for widget in self.master.winfo_children():
            widget.destroy()
        welcome_view = WelcomeView(self.master)
        welcome_view.pack(fill="both", expand=True)
