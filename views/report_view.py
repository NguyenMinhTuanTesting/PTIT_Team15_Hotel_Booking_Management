import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from controllers.report_controller import ReportController

class ReportView(ctk.CTkFrame):
    def __init__(self, master, user=None):
        super().__init__(master, fg_color="#0F0F12")
        self.master = master
        self.user = user
        self.report_controller = ReportController()
        
        self.pie_canvas = None
        self.bar_canvas = None

        # Top Header Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="#18181C", corner_radius=0, height=60)
        self.header_frame.pack(fill="x", side="top")
        
        self.logout_btn = ctk.CTkButton(self.header_frame, text="🚪 ĐĂNG XUẤT", width=120, height=36, font=("Inter", 13, "bold"), fg_color="#DC2626", hover_color="#B91C1C", corner_radius=6, command=self.logout)
        self.logout_btn.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.header_frame, text="📊 BÁO CÁO QUẢN TRỊ & ĐIỀU HÀNH KHÁCH SẠN", font=("Inter", 20, "bold"), text_color="#F8FAFC")
        self.title_label.pack(side="left", expand=True)

        # KPI Summary Cards Frame
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        self.card_avail = self._create_kpi_card(self.kpi_frame, "PHÒNG TRỐNG SẴN SÀNG", "0/32", "Khả dụng nhận khách", "#10B981")
        self.card_avail.pack(side="left", expand=True, fill="x", padx=5)
        
        self.card_checkin = self._create_kpi_card(self.kpi_frame, "ĐANG CÓ KHÁCH (CHECK-IN)", "0", "Đang lưu trú", "#F43F5E")
        self.card_checkin.pack(side="left", expand=True, fill="x", padx=5)
        
        self.card_booked = self._create_kpi_card(self.kpi_frame, "ĐÃ BOOK HÔM NAY", "0", "Lịch nhận phòng", "#F59E0B")
        self.card_booked.pack(side="left", expand=True, fill="x", padx=5)
        
        self.card_service = self._create_kpi_card(self.kpi_frame, "DỌN DẸP / BẢO TRÌ", "0", "Đang xử lý kỹ thuật", "#3B82F6")
        self.card_service.pack(side="left", expand=True, fill="x", padx=5)

        # Main Dashboard Grid (50% Left Column vs 50% Right Column)
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # COLUMN 1 (50% LEFT): 🏨 HIỆN TRẠNG PHÒNG THỜI GIAN THỰC
        # -------------------------------------------------------------
        self.col1_frame = ctk.CTkFrame(self.grid_frame, fg_color="#18181C", corner_radius=12, border_width=1, border_color="#27272A")
        self.col1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        col1_header = ctk.CTkFrame(self.col1_frame, fg_color="#27272A", corner_radius=8)
        col1_header.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(col1_header, text="🏨 HIỆN TRẠNG PHÒNG THỜI GIAN THỰC", font=("Inter", 13, "bold"), text_color="#38BDF8").pack(side="left", padx=10, pady=6)

        # Donut Chart at top of Column 1
        self.pie_chart_frame = ctk.CTkFrame(self.col1_frame, fg_color="#121215", corner_radius=8, border_width=1, border_color="#27272A", height=240)
        self.pie_chart_frame.pack(fill="x", padx=12, pady=(0, 10))

        # Room details inventory at bottom of Column 1
        self.room_details_scroll = ctk.CTkScrollableFrame(self.col1_frame, fg_color="#121215", corner_radius=8, border_width=1, border_color="#27272A")
        self.room_details_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # -------------------------------------------------------------
        # COLUMN 2 (50% RIGHT): 💵 BÁO CÁO & PHÂN TÍCH DOANH THU
        # -------------------------------------------------------------
        self.col2_frame = ctk.CTkFrame(self.grid_frame, fg_color="#18181C", corner_radius=12, border_width=1, border_color="#27272A")
        self.col2_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        col2_header = ctk.CTkFrame(self.col2_frame, fg_color="#27272A", corner_radius=8)
        col2_header.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(col2_header, text="💵 BÁO CÁO & PHÂN TÍCH DOANH THU", font=("Inter", 13, "bold"), text_color="#38BDF8").pack(side="left", padx=10, pady=6)

        filter_sub = ctk.CTkFrame(col2_header, fg_color="transparent")
        filter_sub.pack(side="right", padx=6)
        ctk.CTkLabel(filter_sub, text="Chế độ:", font=("Inter", 11, "bold"), text_color="#94A3B8").pack(side="left", padx=4)
        self.filter_var = ctk.StringVar(value="Theo Ngày")
        self.filter_dropdown = ctk.CTkOptionMenu(filter_sub, values=["Theo Ngày", "Theo Tuần", "Theo Tháng"], variable=self.filter_var, command=self.update_chart, width=115, height=28, fg_color="#0F172A", button_color="#1E293B", button_hover_color="#334155")
        self.filter_dropdown.pack(side="left")

        # Revenue Bar Chart at top of Column 2
        self.bar_chart_frame = ctk.CTkFrame(self.col2_frame, fg_color="#121215", corner_radius=8, border_width=1, border_color="#27272A", height=240)
        self.bar_chart_frame.pack(fill="x", padx=12, pady=(0, 10))

        # Room Type Breakdown at bottom of Column 2
        self.room_type_scroll = ctk.CTkScrollableFrame(self.col2_frame, fg_color="#121215", corner_radius=8, border_width=1, border_color="#27272A")
        self.room_type_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.update_chart("Theo Ngày")

    def _create_kpi_card(self, parent, title, value_text, subtitle, color):
        card = ctk.CTkFrame(parent, fg_color="#18181C", corner_radius=10, border_width=1, border_color="#27272A")
        
        lbl_t = ctk.CTkLabel(card, text=title, font=("Inter", 11, "bold"), text_color="#94A3B8")
        lbl_t.pack(pady=(10, 2), padx=12)
        
        lbl_v = ctk.CTkLabel(card, text=value_text, font=("Inter", 22, "bold"), text_color=color)
        lbl_v.pack(pady=(0, 2), padx=12)
        card.value_label = lbl_v
        
        lbl_sub = ctk.CTkLabel(card, text=subtitle, font=("Inter", 10), text_color="#64748B")
        lbl_sub.pack(pady=(0, 10), padx=12)
        card.sub_label = lbl_sub
        
        return card

    def update_chart(self, filter_val):
        if self.pie_canvas:
            self.pie_canvas.get_tk_widget().destroy()
        if self.bar_canvas:
            self.bar_canvas.get_tk_widget().destroy()
            
        period_map = {"Theo Ngày": "day", "Theo Tuần": "week", "Theo Tháng": "month"}
        period = period_map.get(filter_val, "day")
        
        labels, revenue, room_stats, room_lists, room_type_stats, chart_title = self.report_controller.get_report_data(period)
        
        total_rooms = sum(room_stats.values()) or 32
        avail_cnt = room_stats.get("Trống", 0)
        checkin_cnt = room_stats.get("Đã check in", 0)
        booked_cnt = room_stats.get("Đã book", 0)
        service_cnt = room_stats.get("Đang vệ sinh", 0) + room_stats.get("Bảo trì", 0) + room_stats.get("Đã check out", 0)

        # Update KPI Cards
        pct_avail = (avail_cnt / total_rooms * 100) if total_rooms > 0 else 0
        self.card_avail.value_label.configure(text=f"{avail_cnt} / {total_rooms}")
        self.card_avail.sub_label.configure(text=f"{pct_avail:.1f}% khả dụng")
        
        self.card_checkin.value_label.configure(text=f"{checkin_cnt}")
        self.card_booked.value_label.configure(text=f"{booked_cnt}")
        self.card_service.value_label.configure(text=f"{service_cnt}")

        # -------------------------------------------------------------
        # COLUMN 1 BOTTOM: Update Room Inventory Details Scrollable
        # -------------------------------------------------------------
        for w in self.room_details_scroll.winfo_children():
            w.destroy()

        sections = [
            ("🟢 PHÒNG TRỐNG SẴN SÀNG", "Trống", "#10B981", "#064E3B", "#6EE7B7"),
            ("🟡 ĐÃ BOOK HÔM NAY", "Đã book", "#F59E0B", "#78350F", "#FDE68A"),
            ("🔴 ĐANG CÓ KHÁCH (CHECK-IN)", "Đã check in", "#F43F5E", "#881337", "#FECDD3"),
            ("🟣 ĐÃ CHECK-OUT", "Đã check out", "#818CF8", "#312E81", "#C7D2FE"),
            ("🔵 ĐANG VỆ SINH", "Đang vệ sinh", "#3B82F6", "#1E3A8A", "#BFDBFE"),
            ("⚙️ ĐANG BẢO TRÌ", "Bảo trì", "#64748B", "#1E293B", "#CBD5E1")
        ]

        for title, key, accent_color, bg_pill, txt_pill in sections:
            items = room_lists.get(key, [])
            count = len(items)
            
            grp_box = ctk.CTkFrame(self.room_details_scroll, fg_color="#18181C", corner_radius=8, border_width=1, border_color="#27272A")
            grp_box.pack(fill="x", padx=4, pady=3)
            
            ctk.CTkLabel(grp_box, text=f"{title} ({count})", font=("Inter", 11, "bold"), text_color=accent_color).pack(anchor="w", padx=8, pady=(4, 2))
            
            pills_frame = ctk.CTkFrame(grp_box, fg_color="transparent")
            pills_frame.pack(fill="x", padx=8, pady=(0, 4))

            if items:
                p_row, p_col = 0, 0
                for item in items:
                    pill = ctk.CTkFrame(pills_frame, fg_color=bg_pill, corner_radius=10, border_width=1, border_color=accent_color)
                    pill.grid(row=p_row, column=p_col, padx=2, pady=2, sticky="w")
                    ctk.CTkLabel(pill, text=item, font=("Inter", 9, "bold"), text_color=txt_pill).pack(padx=6, pady=1)
                    p_col += 1
                    if p_col >= 4: # 4 pills per row for crisp compact fit
                        p_col = 0
                        p_row += 1
            else:
                ctk.CTkLabel(pills_frame, text="Chưa có phòng nào", font=("Inter", 9, "italic"), text_color="#64748B").pack(anchor="w")

        # -------------------------------------------------------------
        # COLUMN 2 BOTTOM: Update Room Type Breakdown Scrollable
        # -------------------------------------------------------------
        for w in self.room_type_scroll.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.room_type_scroll, text="📊 CÔNG SUẤT & TỶ LỆ TRỐNG THEO HẠNG PHÒNG", font=("Inter", 12, "bold"), text_color="#38BDF8").pack(anchor="w", padx=6, pady=(4, 6))

        for t_name, t_info in room_type_stats.items():
            tot = t_info["total"]
            avail = t_info["available"]
            pct = (avail / tot * 100) if tot > 0 else 0
            
            t_box = ctk.CTkFrame(self.room_type_scroll, fg_color="#18181C", corner_radius=8, border_width=1, border_color="#27272A")
            t_box.pack(fill="x", padx=4, pady=3)

            header_row = ctk.CTkFrame(t_box, fg_color="transparent")
            header_row.pack(fill="x", padx=8, pady=(6, 2))
            
            ctk.CTkLabel(header_row, text=f"Hạng {t_name}", font=("Inter", 11, "bold"), text_color="#F8FAFC").pack(side="left")
            ctk.CTkLabel(header_row, text=f"{avail}/{tot} trống ({pct:.0f}%)", font=("Inter", 11, "bold"), text_color="#10B981" if pct > 50 else "#F59E0B").pack(side="right")

            # Progress Bar visual
            prog = ctk.CTkProgressBar(t_box, height=6, corner_radius=3, fg_color="#0F172A", progress_color="#10B981" if pct > 50 else "#F59E0B")
            prog.pack(fill="x", padx=8, pady=(0, 6))
            prog.set(avail / tot if tot > 0 else 0)

        # -------------------------------------------------------------
        # COLUMN 1 TOP: Canvas 1 - Donut Chart (Matplotlib)
        # -------------------------------------------------------------
        fig_pie, ax_pie = plt.subplots(figsize=(4.5, 2.5), facecolor='#121215')
        fig_pie.patch.set_facecolor('#121215')
        ax_pie.set_facecolor('#121215')

        r_labels = []
        r_sizes = []
        r_colors = []
        color_map = {"Trống": "#10B981", "Đã book": "#F59E0B", "Đã check in": "#F43F5E", "Đã check out": "#818CF8", "Đang vệ sinh": "#3B82F6", "Bảo trì": "#64748B"}

        for k, v in room_stats.items():
            if v > 0:
                r_labels.append(k)
                r_sizes.append(v)
                r_colors.append(color_map.get(k, "#FFFFFF"))

        if r_sizes:
            total = sum(r_sizes)
            legend_labels = [f"{l} ({s/total*100:.1f}%)" for l, s in zip(r_labels, r_sizes)]
            wedges, texts = ax_pie.pie(r_sizes, colors=r_colors, startangle=90, wedgeprops=dict(width=0.4, edgecolor='#121215'))
            ax_pie.legend(wedges, legend_labels, loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=3, frameon=False, labelcolor="white", fontsize=8)
        
        ax_pie.set_title("Tỷ lệ phòng hiện tại", color="white", fontsize=11, fontweight='bold')
        fig_pie.tight_layout(pad=1.2)

        self.pie_canvas = FigureCanvasTkAgg(fig_pie, master=self.pie_chart_frame)
        self.pie_canvas.draw()
        self.pie_canvas.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)

        # -------------------------------------------------------------
        # COLUMN 2 TOP: Canvas 2 - Revenue Bar Chart (Matplotlib)
        # -------------------------------------------------------------
        fig_bar, ax_bar = plt.subplots(figsize=(5.0, 2.5), facecolor='#121215')
        fig_bar.patch.set_facecolor('#121215')
        ax_bar.set_facecolor('#121215')

        if not labels:
            labels = ["N/A"]
            revenue = [0]

        bars = ax_bar.bar(labels, revenue, color='#38BDF8', width=0.45)
        ax_bar.set_title(chart_title, color="white", fontsize=11, fontweight='bold')

        bar_labels = [f"{int(r):,} VNĐ".replace(',', '.') if r > 0 else "" for r in revenue]
        ax_bar.bar_label(bars, labels=bar_labels, color='white', padding=3, fontsize=8, fontweight='bold')

        ax_bar.tick_params(colors='#94A3B8', axis='y', labelsize=8)
        if period == 'day' and len(labels) > 10:
            ax_bar.tick_params(colors='#F8FAFC', axis='x', labelsize=7, rotation=45)
        else:
            ax_bar.tick_params(colors='#F8FAFC', axis='x', labelsize=8, rotation=0)

        def money_formatter(x, pos):
            return f"{int(x):,} VNĐ".replace(',', '.')

        ax_bar.yaxis.set_major_formatter(plt.FuncFormatter(money_formatter))

        for spine in ax_bar.spines.values():
            spine.set_edgecolor('#27272A')

        fig_bar.tight_layout(pad=1.2)

        self.bar_canvas = FigureCanvasTkAgg(fig_bar, master=self.bar_chart_frame)
        self.bar_canvas.draw()
        self.bar_canvas.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)

    def logout(self):
        from views.welcome_view import WelcomeView
        for widget in self.master.winfo_children():
            widget.destroy()
        welcome_view = WelcomeView(self.master)
        welcome_view.pack(fill="both", expand=True)
