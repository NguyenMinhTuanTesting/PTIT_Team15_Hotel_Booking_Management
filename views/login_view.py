import customtkinter as ctk
from controllers.auth_controller import AuthController

class LoginView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#121212")
        self.master = master
        self.auth_controller = AuthController()

        self.login_frame = ctk.CTkFrame(self, width=400, height=450, fg_color="#1E1E1E", corner_radius=15)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self.login_frame, text="ĐĂNG NHẬP HỆ THỐNG", font=("Inter", 24, "bold"), text_color="#FFFFFF")
        self.title_label.place(relx=0.5, rely=0.15, anchor="center")

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Tên đăng nhập", width=300, height=45, font=("Inter", 14), fg_color="#121212", border_color="#333333")
        self.username_entry.place(relx=0.5, rely=0.35, anchor="center")

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Mật khẩu", show="*", width=300, height=45, font=("Inter", 14), fg_color="#121212", border_color="#333333")
        self.password_entry.place(relx=0.5, rely=0.55, anchor="center")

        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="#FF4C4C", font=("Inter", 12))
        self.error_label.place(relx=0.5, rely=0.68, anchor="center")

        self.login_btn = ctk.CTkButton(self.login_frame, text="ĐĂNG NHẬP", width=300, height=45, font=("Inter", 16, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", command=self.handle_login)
        self.login_btn.place(relx=0.5, rely=0.8, anchor="center")
        
        self.back_btn = ctk.CTkButton(self, text="QUAY LẠI", width=120, height=40, font=("Inter", 14, "bold"), fg_color="transparent", border_width=1, border_color="#333333", hover_color="#1E1E1E", command=self.go_back)
        self.back_btn.place(relx=0.05, rely=0.05)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        success, user = self.auth_controller.login(username, password)
        if success:
            self.error_label.configure(text="Đăng nhập thành công!", text_color="#10B981")
            self.after(500, lambda: self.open_dashboard(user))
        else:
            self.error_label.configure(text="Sai tên đăng nhập hoặc mật khẩu", text_color="#EF4444")

    def open_dashboard(self, user):
        for widget in self.master.winfo_children():
            widget.destroy()
            
        if user.get("role") == "admin":
            from views.report_view import ReportView
            view = ReportView(self.master, user)
        else:
            from views.dashboard_view import DashboardView
            view = DashboardView(self.master, user)
            
        view.pack(fill="both", expand=True)

    def go_back(self):
        from views.welcome_view import WelcomeView
        for widget in self.master.winfo_children():
            widget.destroy()
        welcome_view = WelcomeView(self.master)
        welcome_view.pack(fill="both", expand=True)
