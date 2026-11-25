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
- **Bình luận thời gian thực (WebSocket)**:
  - Nhiều máy trong cùng mạng LAN thấy bình luận của nhau ngay lập tức, không cần tải lại.
  - Mất mạng vẫn bình luận được (lưu JSON như cũ), có mạng lại thì tự kết nối và gửi bù.
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

### 4. Bật bình luận thời gian thực trong mạng LAN (tùy chọn)
Trên **một** máy làm server (xem IP bằng `ipconfig` / `ip a`):
```bash
cd kaban-app
python chat_server.py            # lắng nghe 0.0.0.0:8765
```
Trên mỗi máy chạy ứng dụng (kể cả máy server):
```bash
python main.py --chat ws://192.168.1.10:8765     # thay bằng IP máy server
```
Hoặc đặt biến môi trường `KANBAN_CHAT_URL=ws://192.168.1.10:8765`. Khung bình luận hiện
`● Trực tuyến` khi đã kết nối. Không truyền `--chat` thì ứng dụng chạy ngoại tuyến như trước.
Nếu Windows Firewall hỏi, hãy cho phép Python nhận kết nối trong mạng riêng (Private).

Giao thức: mỗi công việc là một "phòng" `DA-xxx/CV-xxx`; tin nhắn là JSON (`vao_phong`, `binh_luan`,
`xoa_binh_luan`, `lich_su`, `loi`), xem `services/chat_protocol.py`. Server giữ 50 bình luận gần nhất
mỗi phòng và nối thêm mọi sự kiện vào `data/chat_log.jsonl`. Server tin tên người gửi do máy khách
khai báo, nên chỉ dùng trong mạng LAN tin cậy để demo.

### 5. Tài khoản dùng thử (Mặc định)
Hệ thống cung cấp sẵn các tài khoản mẫu (mật khẩu mặc định: `123456`):
- `admin` (Quản trị viên hệ thống)
- `quoc` (Thành viên)
- `huy` (Thành viên)
- `khoa` (Thành viên)
- `phu` (Thành viên)

---

## 🧪 Kiểm thử tự động (Unit Tests)

Chạy toàn bộ unit tests (gồm test WebSocket chạy server thật trên localhost):
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
    ├── main.py                 # Điểm khởi chạy ứng dụng (cờ --chat để bật realtime)
    ├── chat_server.py          # Server WebSocket chuyển tiếp bình luận trong LAN
    ├── config.py               # Các hằng số cấu hình hệ thống
    ├── exceptions.py           # Phân cấp ngoại lệ tùy chỉnh
    ├── logger.py               # Cấu hình ghi log ứng dụng
    ├── requirements.txt        # Danh sách thư viện Python
    ├── data/                   # Dữ liệu cục bộ: du_an.json (dự án + công việc), du_lieu_moc.json (người dùng), nhat_ky.jsonl (nhật ký append-only), viec_chua_hoan_thanh.jsonl (việc hủy / chưa hoàn thành append-only) và backup/
    ├── models/                 # Các thực thể dữ liệu (Dự án, Công việc, Người dùng)
    ├── services/               # Nghiệp vụ (Xác thực, Lưu trữ, Thống kê, API)
    ├── ui/                     # Giao diện người dùng
    │   ├── components/         # Sidebar, Topbar, Task Card, Column Widget
    │   ├── dialogs/            # Dialog thêm/sửa việc, đổi mật khẩu, dự án
    │   ├── styles/             # Màu sắc, font chữ và theme
    │   └── views/              # Kanban Board view, Stats view
    └── tests/                  # Bộ kiểm thử tự động (OOP, Storage, Baseline, API)
```
