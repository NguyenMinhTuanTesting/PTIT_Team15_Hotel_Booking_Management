import customtkinter as ctk
import re
from datetime import datetime
import datetime as dt_module
from controllers.room_controller import RoomController
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

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user=None):
        super().__init__(master, fg_color="#121212")
        self.master = master
        self.user = user
        self.room_controller = RoomController()
        
        self.title_label = ctk.CTkLabel(self, text="SƠ ĐỒ PHÒNG (Nhân viên)", font=("Inter", 24, "bold"), text_color="#FFFFFF")
        self.title_label.pack(pady=(20, 10))

        self.logout_btn = ctk.CTkButton(self, text="ĐĂNG XUẤT", width=120, height=40, font=("Inter", 14, "bold"), fg_color="transparent", border_width=1, border_color="#333333", hover_color="#1E1E1E", command=self.logout)
        self.logout_btn.place(relx=0.05, rely=0.05)

        self.search_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        self.search_frame.pack(pady=10, padx=20, fill="x")
        
        hours = [f"{i:02d}" for i in range(24)]
        minutes = ["00", "15", "30", "45"]
        
        ci_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        ci_frame.pack(side="left", padx=10, pady=10)
        
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

        co_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        co_frame.pack(side="left", padx=10, pady=10)
        
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

        self.search_btn = ctk.CTkButton(self.search_frame, text="TÌM PHÒNG", font=("Inter", 14, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", command=self.load_rooms)
        self.search_btn.pack(side="right", padx=20, pady=10)

        self.error_label = ctk.CTkLabel(self, text="", text_color="#EF4444", font=("Inter", 12))
        self.error_label.pack()

        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.status_colors = {
            "Trống": "#22C55E",
            "Đã book": "#EAB308",
            "Đã check in": "#EF4444",
            "Đã check out": "#6366F1",
            "Đang vệ sinh": "#3B82F6",
            "Bảo trì": "#6B7280"
        }
        
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

    def load_rooms(self):
        check_in = self.check_in_entry.get().strip()
        check_out = self.check_out_entry.get().strip()
        
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", check_in) or not re.match(r"^\d{2}-\d{2}-\d{4}$", check_out):
            self.error_label.configure(text="Định dạng ngày không hợp lệ")
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
        
        self.room_controller.get_rooms_status_by_time(ci_str, co_str, self.on_rooms_loaded)

    def on_rooms_loaded(self, rooms):
        self.after(0, self.render_grid, rooms)

    def render_grid(self, rooms):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        columns = 8
        for i, room_data in enumerate(rooms):
            status = room_data.get("status", "Trống")
            color = self.status_colors.get(status, "#6B7280")
            
            display_text = f"{room_data['room_number']}\n{status}"
            if room_data.get('customer_name'):
                display_text += f"\n({room_data['customer_name']})"
                
            btn = ctk.CTkButton(
                self.grid_frame, 
                text=display_text, 
                width=120, height=100, 
                font=("Inter", 12, "bold"),
                fg_color=color,
                hover_color=color,
                command=lambda r=room_data: self.open_room_popup(r)
            )
            btn.grid(row=i // columns, column=i % columns, padx=10, pady=10)

    def open_room_popup(self, room_data):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Tác vụ phòng {room_data['room_number']}")
        popup.geometry("350x400")
        popup.attributes("-topmost", True)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Phòng {room_data['room_number']} - {room_data['room_type']}", font=("Inter", 18, "bold")).pack(pady=(15, 5))
        ctk.CTkLabel(popup, text=f"Trạng thái: {room_data['status']}", font=("Inter", 14)).pack(pady=(0, 15))
        
        ci_str = self.current_ci_dt.strftime("%Y-%m-%d %H:%M:%S")
        co_str = self.current_co_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        if room_data['status'] == 'Trống':
            ctk.CTkButton(
                popup, text="Đánh dấu Bảo trì", fg_color="#6B7280", hover_color="#4B5563",
                command=lambda: [self.room_controller.mark_maintenance(room_data['room_id'], ci_str, co_str, lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=10)
        elif room_data['status'] == 'Bảo trì':
            ctk.CTkButton(
                popup, text="Hủy Bảo trì", fg_color="#22C55E", hover_color="#16A34A",
                command=lambda: [self.room_controller.remove_maintenance(room_data['booking_id'], lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=10)
        elif room_data['status'] == 'Đã book':
            ctk.CTkButton(
                popup, text="Khách Check-in", fg_color="#EF4444", hover_color="#DC2626",
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CHECKED_IN', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=10)
            ctk.CTkButton(
                popup, text="Khách Không Tới (Hủy)", fg_color="#6B7280", hover_color="#4B5563",
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CANCELLED', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=10)
        elif room_data['status'] == 'Đã check in':
            ctk.CTkButton(
                popup, text="Khách Check-out", fg_color="#475569", hover_color="#334155",
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CHECKED_OUT', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=10)
        elif room_data['status'] == 'Đã check out':
            ctk.CTkButton(
                popup, text="Bắt đầu vệ sinh", fg_color="#2563EB", hover_color="#1D4ED8",
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'CLEANING', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=10)
        elif room_data['status'] == 'Đang vệ sinh':
            ctk.CTkLabel(popup, text="Đang vệ sinh (Tự động sạch sau 30 phút)", font=("Inter", 12), text_color="#EAB308").pack(pady=5)
            ctk.CTkButton(
                popup, text="Hoàn tất dọn sớm", fg_color="#22C55E", hover_color="#16A34A",
                command=lambda: [self.room_controller.update_booking_status(room_data['booking_id'], 'COMPLETED', lambda _: self.after(0, lambda: [popup.destroy(), self.load_rooms()]))]
            ).pack(pady=10)

    def logout(self):
        from views.welcome_view import WelcomeView
        for widget in self.master.winfo_children():
            widget.destroy()
        welcome_view = WelcomeView(self.master)
        welcome_view.pack(fill="both", expand=True)
