# Hệ Thống Quản Lý Và Phân Tích Kết Quả Học Tập

Ứng dụng desktop viết bằng Python theo mô hình MVC, sử dụng `CustomTkinter` để xây dựng giao diện, `SQLite` để lưu dữ liệu, và `NumPy`/`Matplotlib` để tính toán, thống kê cũng như vẽ biểu đồ.

## Giới Thiệu

Đây là một ứng dụng quản lý sinh viên và học phần, cho phép theo dõi điểm số, tính CPA tự động và thống kê kết quả học tập trực quan.  
Chương trình được xây dựng theo hướng dễ đọc, dễ mở rộng và dễ bảo trì.

## Chức Năng Chính

- Quản lý sinh viên.
- Quản lý học phần.
- Quản lý bảng điểm.
- Xem chi tiết điểm của từng sinh viên.
- Tính CPA và xếp loại tự động.
- Thống kê kết quả học tập bằng biểu đồ tròn và bảng top 10.
- Tìm kiếm, sắp xếp và chọn nhiều dòng bằng checkbox.
- Thêm, sửa, xóa dữ liệu.
- Nhập CSV và xuất CSV cho sinh viên, học phần và bảng điểm.
- Có trang giới thiệu ứng dụng và file hướng dẫn sử dụng PDF.
- Có logger ghi lại hoạt động của chương trình.

## Công Nghệ Sử Dụng

- Python
- CustomTkinter
- Tkinter
- SQLite
- NumPy
- Matplotlib

## Cấu Trúc Dự Án

```text
Tự làm/
├── main.py
├── README.MD
└── app/
    ├── controllers/
    ├── models/
    ├── utils/
    ├── views/
    │   ├── pages/
    │   └── windows/
    ├── data/
    ├── docs/
    └── logs/

```

### Ý nghĩa các thư mục

- `main.py`: điểm khởi động của ứng dụng.
- `app/controllers/`: xử lý nghiệp vụ và điều phối giữa view và model.
- `app/models/`: làm việc với cơ sở dữ liệu SQLite.
- `app/views/`: giao diện người dùng.
- `app/views/pages/`: các trang chính như dashboard, sinh viên, học phần, điểm, thống kê, giới thiệu.
- `app/views/windows/`: các cửa sổ con như form thêm/sửa và xem chi tiết.
- `app/data/`: nơi lưu file cơ sở dữ liệu `.db`.
- `app/docs/`: nơi lưu file hướng dẫn sử dụng PDF.
- `app/logs/`: nơi lưu file log của ứng dụng.

## Cách Chạy

### 1.Tạo môi trường ảo

```bash
python -m venv .venv
```

### 2. Kích hoạt môi trường ảo

```bash
.venv\Scripts\activate
```

### 3. Cài thư viện cần thiết

```bash
pip install -r requirements.txt
```

### 4. Chạy chương trình

```bash
python main.py
```

## Dữ Liệu Và Log

- Dữ liệu của ứng dụng được lưu trong `app/data/app_data.db`.
- File log được ghi trong `app/logs/app.log`.
- Khi chạy lần đầu, ứng dụng sẽ tự tạo database nếu chưa tồn tại.

## Tài Liệu Hướng Dẫn

File PDF hướng dẫn nằm tại:

- `app/docs/Huong_Dan_Su_Dung_Ket_Qua_Hoc_Tap_App.pdf`

## Một Số Tính Năng Nổi Bật

- Sidebar có thể thu gọn/mở rộng.
- Dashboard hiển thị thống kê tổng quan.
- Trang thống kê có biểu đồ tròn và bảng top 10 CPA.
- Trang bảng điểm có thể mở cửa sổ chi tiết cho từng sinh viên.
- Các form nhập dữ liệu có validation cơ bản để kiểm tra dữ liệu đầu vào.
- Có nhập/xuất CSV với tiêu đề tiếng Việt.

## Ghi Chú

- Dự án được viết theo hướng dễ đọc, dễ sửa và dễ mở rộng.
- Logic xử lý được tách rõ giữa giao diện, điều phối và cơ sở dữ liệu theo mô hình MVC.
