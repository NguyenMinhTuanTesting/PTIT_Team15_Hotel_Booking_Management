import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from controllers.report_controller import ReportController

class ReportView(ctk.CTkFrame):
    def __init__(self, master, user=None):
        super().__init__(master, fg_color="#121212")
        self.master = master
        self.user = user
        self.report_controller = ReportController()
        
        self.title_label = ctk.CTkLabel(self, text="BÁO CÁO DOANH THU (QUẢN TRỊ VIÊN)", font=("Inter", 24, "bold"), text_color="#FFFFFF")
        self.title_label.pack(pady=20)
        
        self.logout_btn = ctk.CTkButton(self, text="ĐĂNG XUẤT", width=120, height=40, font=("Inter", 14, "bold"), fg_color="#EF4444", hover_color="#DC2626", command=self.logout)
        self.logout_btn.place(relx=0.05, rely=0.05)

        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(pady=10)
        
        ctk.CTkLabel(self.filter_frame, text="Hiển thị theo:", font=("Inter", 14)).pack(side="left", padx=10)
        self.filter_var = ctk.StringVar(value="Theo Ngày")
        self.filter_dropdown = ctk.CTkOptionMenu(self.filter_frame, values=["Theo Ngày", "Theo Tuần", "Theo Tháng"], variable=self.filter_var, command=self.update_chart)
        self.filter_dropdown.pack(side="left")

        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.canvas = None
        self.update_chart("Theo Ngày")

    def update_chart(self, filter_val):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            
        period_map = {"Theo Ngày": "day", "Theo Tuần": "week", "Theo Tháng": "month"}
        period = period_map.get(filter_val, "day")
        
        labels, revenue, room_stats = self.report_controller.get_report_data(period)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), facecolor='#121212')
        fig.patch.set_facecolor('#121212')
        ax1.set_facecolor('#121212')
        ax2.set_facecolor('#121212')
        
        r_labels = []
        r_sizes = []
        r_colors = []
        color_map = {"Trống": "#22C55E", "Đã book": "#EAB308", "Đã check in": "#EF4444", "Đã check out": "#6366F1", "Đang vệ sinh": "#3B82F6", "Bảo trì": "#6B7280"}
        
        for k, v in room_stats.items():
            if v > 0:
                r_labels.append(k)
                r_sizes.append(v)
                r_colors.append(color_map.get(k, "#FFFFFF"))
                
        if r_sizes:
            total = sum(r_sizes)
            legend_labels = [f"{l} ({s/total*100:.1f}%)" for l, s in zip(r_labels, r_sizes)]
            wedges, texts = ax1.pie(r_sizes, colors=r_colors, startangle=90)
            ax1.legend(wedges, legend_labels, loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False, labelcolor="white")
        ax1.set_title("Trạng thái phòng hiện tại", color="white")
        
        if not labels:
            labels = ["N/A"]
            revenue = [0]
            
        bars = ax2.bar(labels, revenue, color='#3B82F6')
        ax2.set_title(f"Doanh thu ({filter_val})", color="white")
        
        bar_labels = [f"{int(r):,} VNĐ".replace(',', '.') if r > 0 else "" for r in revenue]
        ax2.bar_label(bars, labels=bar_labels, color='white', padding=3)
        
        ax2.tick_params(colors='white', axis='y', labelsize=10)
        ax2.tick_params(colors='white', axis='x', labelsize=10)
        
        # Format y-axis to show money correctly (e.g. 1.000.000 VNĐ)
        def money_formatter(x, pos):
            return f"{int(x):,} VNĐ".replace(',', '.')
            
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(money_formatter))
        
        for spine in ax2.spines.values():
            spine.set_edgecolor('white')

        fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        
        # Force CustomTkinter to recalculate geometry so the canvas fits the screen
        def force_resize():
            self.master.update_idletasks()
            w = self.chart_frame.winfo_width()
            h = self.chart_frame.winfo_height()
            if w > 1 and h > 1:
                canvas_widget.event_generate("<Configure>", width=w, height=h)
                
        self.after(50, force_resize)

    def logout(self):
        from views.welcome_view import WelcomeView
        for widget in self.master.winfo_children():
            widget.destroy()
        welcome_view = WelcomeView(self.master)
        welcome_view.pack(fill="both", expand=True)
