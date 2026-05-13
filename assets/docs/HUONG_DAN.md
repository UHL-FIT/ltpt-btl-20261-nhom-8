# Hướng Dẫn Sử Dụng

## Chạy ứng dụng

```powershell
cd Group_8\Ket_Qua_Hoc_Tap_App
python main.py
```

## Luồng chính

1. Mở Dashboard.
2. Vào **Quản lý sinh viên** để thêm hoặc import danh sách sinh viên.
3. Vào **Quản lý học phần** để khai báo học phần và số tín chỉ.
4. Vào **Quản lý bảng điểm** để nhập điểm theo học kỳ, năm học.
5. Double-click một sinh viên trong bảng điểm để xem chi tiết.
6. Vào **Thống kê & biểu đồ** để xem GPA trung bình, phân bố xếp loại và top GPA.

## CSV Template

- `templates/sinhvien_template.csv`
- `templates/monhoc_template.csv`
- `templates/bangdiem_template.csv`

File CSV nên lưu UTF-8 hoặc UTF-8-SIG để hiển thị tiếng Việt tốt trong Excel.
