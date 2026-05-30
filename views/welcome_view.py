import customtkinter as ctk

class WelcomeView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#121212")
        self.master = master
        
        self.title_label = ctk.CTkLabel(self, text="HỆ THỐNG QUẢN LÝ KHÁCH SẠN", font=("Inter", 36, "bold"), text_color="#FFFFFF")
        self.title_label.place(relx=0.5, rely=0.3, anchor="center")

        self.customer_btn = ctk.CTkButton(self, text="DÀNH CHO KHÁCH HÀNG", width=350, height=55, font=("Inter", 16, "bold"), fg_color="#27272A", hover_color="#3F3F46", command=self.show_guest_booking)
        self.customer_btn.place(relx=0.5, rely=0.5, anchor="center")

        self.internal_btn = ctk.CTkButton(self, text="ĐĂNG NHẬP NỘI BỘ", width=350, height=55, font=("Inter", 16, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", command=self.show_login)
        self.internal_btn.place(relx=0.5, rely=0.6, anchor="center")

    def show_login(self):
        from views.login_view import LoginView
        for widget in self.master.winfo_children():
            widget.destroy()
        login_view = LoginView(self.master)
        login_view.pack(fill="both", expand=True)

    def show_guest_booking(self):
        from views.guest_booking_view import GuestBookingView
        for widget in self.master.winfo_children():
            widget.destroy()
        guest_view = GuestBookingView(self.master)
        guest_view.pack(fill="both", expand=True)
