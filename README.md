# 🏨 Hệ Thống Quản Lý Đặt Phòng Khách Sạn (Hotel Booking Management System)

Đây là mã nguồn dự án **Quản Lý Đặt Phòng Khách Sạn**, được phát triển dưới dạng phần mềm Desktop App dành cho Đồ án môn học **Nhập Môn Công Nghệ Phần Mềm**.

🏫 **Đơn vị:** Học viện Công nghệ Bưu chính Viễn thông Cơ sở TP.HCM (PTIT HCM)  
👥 **Nhóm thực hiện:** Nhóm 15  
🧑‍💻 **Thành viên:**
1. Nguyễn Minh Tuấn
2. Hoàng Văn Thái

---

## 🚀 Giới thiệu chung
Hệ thống cung cấp giải pháp quản lý khách sạn toàn diện, mô phỏng chính xác quy trình vận hành thực tế thông qua **Vòng đời phòng 6 bước**. Phần mềm được thiết kế với giao diện Dark Mode hiện đại, tích hợp biểu đồ thống kê theo thời gian thực (Real-time).

### ✨ Các tính năng nổi bật
* **Phân quyền người dùng:** Khách hàng (Đặt phòng tự động qua Web/App giả lập), Nhân viên (Staff), và Quản trị viên (Admin).
* **Vòng đời phòng chuẩn nghiệp vụ (6 Bước):** `Trống` ➡️ `Đã book` ➡️ `Đã check-in` ➡️ `Đã check-out` ➡️ `Đang vệ sinh` ➡️ `Trống` (hoặc `Bảo trì`).
* **Hệ thống chạy ngầm (Background Worker):** Tự động đếm ngược 30 phút dọn vệ sinh để chuyển phòng sang trạng thái trống. 
* **Quản trị hệ thống (Admin Dashboard):**
  * Biểu đồ Doanh thu (Bar chart) tự động quy đổi và nhóm theo Ngày/Tuần/Tháng.
  * Biểu đồ Tròn (Pie chart) thống kê tình trạng sử dụng phòng Real-time.
* **Gửi Email Tự động:** Gửi hóa đơn xác nhận booking cho khách hàng thông qua SMTP.

---

## 🛠️ Công nghệ sử dụng
* **Ngôn ngữ:** Python 3.x
* **Giao diện (GUI):** `CustomTkinter`, `tkcalendar` (Dark Mode chuẩn hiện đại).
* **Cơ sở dữ liệu:** `MySQL` (Sử dụng thư viện `mysql-connector-python`).
* **Trực quan hóa Dữ liệu:** `Matplotlib` (Nhúng trực tiếp vào giao diện Tkinter).
* **Email Service:** `smtplib` & `email.mime` (Gửi email tự động).

---

## ⚙️ Hướng dẫn Cài đặt & Chạy ứng dụng

### Bước 1: Cài đặt thư viện
Bạn cần có Python 3 (khuyến nghị 3.9+). Clone dự án về và chạy lệnh:
```bash
pip install customtkinter mysql-connector-python matplotlib tkcalendar python-dotenv
```

### Bước 2: Thiết lập Database
1. Mở MySQL (XAMPP, MySQL Workbench, v.v...).
2. Tạo database mới (ví dụ: `hotel_booking_db`).
3. Import file `docs/database_schema.sql` vào cơ sở dữ liệu vừa tạo.

### Bước 3: Cấu hình hệ thống (Biến môi trường)
Tạo một file `.env` ở thư mục gốc của dự án và điền thông tin sau:
```env
DB_HOST=localhost
DB_USER=root
DB_PASS=
DB_NAME=hotel_booking_db

EMAIL_ADDRESS=email_cua_ban@gmail.com
EMAIL_PASSWORD=mat_khau_ung_dung
```

### Bước 4: Khởi chạy
Tại thư mục gốc, chạy lệnh sau để khởi động hệ thống:
```bash
python main.py
```

*Tài khoản mặc định:*
* **Admin:** `admin` / `admin`
* **Staff:** `staff` / `staff`

---

## 📝 Giấy phép (License)
Dự án được xây dựng nhằm mục đích học tập và phục vụ báo cáo Đồ án môn học tại PTIT TP.HCM. Không sử dụng cho mục đích thương mại khi chưa có sự cho phép.

© 2026 PTIT HCM - Team 15. All Rights Reserved.
