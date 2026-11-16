# Kanban App — Quản lý công việc và quy trình (Python / Tkinter)

Đồ án môn học: Xây dựng ứng dụng quản lý công việc theo mô hình Kanban Board bằng Python, giao diện đồ họa Tkinter / CustomTkinter và lưu trữ dữ liệu JSON.

---

## 🌟 Tính năng nổi bật

- **Quản lý dự án**: Tạo mới, chọn dự án, phân quyền truy cập, quản lý thành viên tham gia, xóa dự án (dành cho Quản trị viên).
- **Bảng Kanban trực quan**: Hiển thị các cột trạng thái (*Cần làm*, *Đang làm*, *Kiểm tra*, *Hoàn thành*), hỗ trợ kéo thả thẻ hoặc chuyển nhanh cột.
- **Quản lý công việc (CRUD)**:
  - Thêm, sửa, xem chi tiết, xóa công việc.
  - Phân loại công việc thường (`CongViecThuong`) và công việc khẩn (`CongViecKhan`) áp dụng tính kế thừa và đa hình OOP.
  - Bình luận và trao đổi trực tiếp trên từng công việc.
- **Xác thực & Bảo mật tài khoản**:
  - Đăng nhập, đăng ký thành viên mới.
  - **Đổi mật khẩu** an toàn ngay trên giao diện (mật khẩu băm SHA-256 kèm salt ngẫu nhiên).
  - Phân quyền theo vai trò: `QuanTriVien` và `ThanhVien`.
- **Thống kê & Báo cáo**:
  - Biểu đồ phân bổ tiến độ bằng Canvas trực quan, KPI tổng hợp.
  - Bảng cảnh báo hạn chót và nhật ký hoạt động hệ thống.
  - **Xuất báo cáo tiến độ ra file** (`.txt` hoặc `.csv`).
- **Tích hợp API ngoài**:
  - Tải và đồng bộ công việc mẫu tự động từ DummyJSON Todos API.
- **An toàn lưu trữ**:
  - Đọc/ghi JSON nguyên tử (`atomic write`).
  - Tự động sao lưu (`backup/`) và phục hồi khi phát hiện file hỏng.

---

## 🚀 Hướng dẫn cài đặt & Chạy ứng dụng

### 1. Yêu cầu hệ thống
- Python 3.8+ (khuyên dùng Python 3.10 – 3.12/3.14).
- Hệ điều hành: Windows / macOS / Linux.

### 2. Cài đặt thư viện phụ thuộc
Mở terminal tại thư mục gốc hoặc thư mục `kaban-app`:
```bash
cd kaban-app
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python main.py
```

### 4. Tài khoản dùng thử (Mặc định)
Hệ thống cung cấp sẵn các tài khoản mẫu (mật khẩu mặc định: `123456`):
- `admin` (Quản trị viên hệ thống)
- `quoc` (Thành viên)
- `huy` (Thành viên)
- `khoa` (Thành viên)
- `phu` (Thành viên)

---

## 🧪 Kiểm thử tự động (Unit Tests)

Chạy toàn bộ 82 unit tests:
```bash
cd kaban-app
python -m unittest discover tests
```

---

## 📁 Cấu trúc thư mục

```
project_python/
├── PHAN_CONG_NHIEM_VU.md       # Bảng phân công nhiệm vụ đồ án
├── README.md                   # Hướng dẫn đồ án tổng quan
└── kaban-app/
    ├── main.py                 # Điểm khởi chạy ứng dụng
    ├── config.py               # Các hằng số cấu hình hệ thống
    ├── exceptions.py           # Phân cấp ngoại lệ tùy chỉnh
    ├── logger.py               # Cấu hình ghi log ứng dụng
    ├── requirements.txt        # Danh sách thư viện Python
    ├── data/                   # File dữ liệu JSON và thư mục backup
    ├── models/                 # Các thực thể dữ liệu (Dự án, Công việc, Người dùng)
    ├── services/               # Nghiệp vụ (Xác thực, Lưu trữ, Thống kê, API)
    ├── ui/                     # Giao diện người dùng
    │   ├── components/         # Sidebar, Topbar, Task Card, Column Widget
    │   ├── dialogs/            # Dialog thêm/sửa việc, đổi mật khẩu, dự án
    │   ├── styles/             # Màu sắc, font chữ và theme
    │   └── views/              # Kanban Board view, Stats view
    └── tests/                  # Bộ kiểm thử tự động (OOP, Storage, Baseline, API)
```
