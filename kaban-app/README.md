# Ứng dụng quản lý công việc Kanban

Ứng dụng desktop Python/CustomTkinter dùng JSON cục bộ. Chạy từ thư mục `kaban-app`:

```powershell
pip install -r requirements.txt
python main.py
python -m unittest discover -s tests
```

Tài khoản mẫu khi chưa có file dữ liệu: `admin / 123456` và `khoa / 123456`. Hãy đổi mật khẩu mẫu trước khi dùng dữ liệu thật.

## Chức năng

- Dự án, cột Kanban, công việc thường/khẩn, bình luận, tìm kiếm/lọc và kéo thả.
- Admin quản lý tài khoản, cấp hoặc thu hồi Leader, khóa tài khoản, phân thành viên vào nhóm. Mỗi dự án có thể có nhiều Leader; mỗi thành viên thuộc tối đa một nhóm.
- Việc do thành viên tạo chờ Leader nhóm duyệt; việc do Leader tạo chờ Admin duyệt. Việc chờ duyệt không hiện trên bảng.
- Người phụ trách có thể xin mở lại việc hoàn thành hoặc gia hạn việc quá hạn. Người có quyền duyệt xác nhận yêu cầu; gia hạn tối đa ba lần.
- Hủy công việc là xóa mềm: giữ dữ liệu, lý do và thời gian hủy; có màn hình khôi phục. Nhật ký JSONL nối thêm nằm cạnh `data/nhat_ky.json`.
- Gỡ thành viên bị chặn nếu còn việc chưa hoàn thành; việc hoàn thành giữ tên người phụ trách đã rời dự án.
- Thống kê, báo cáo TXT/CSV; nhập công việc mẫu từ DummyJSON Todos. API bổ sung: ngày lễ Việt Nam của Tallyfy để tính hạn làm việc, câu động viên DummyJSON, tài khoản demo JSONPlaceholder.

## Cấu trúc chính

- `models/`: dự án, công việc, người dùng và bình luận.
- `services/`: nghiệp vụ, lưu JSON/backup, API và nhật ký.
- `ui/`: giao diện Kanban, các dialog và thống kê.
- `tests/`: kiểm thử tự động. Dùng `python -m unittest discover -s tests` để xem số ca và kết quả hiện tại.
- `data/`: dữ liệu cục bộ:
  - `data/du_an.json`: dữ liệu dự án và công việc.
  - `data/du_lieu_moc.json`: tài khoản người dùng (mật khẩu đã băm SHA-256 + salt) và yêu cầu sửa thông tin.
  - `data/nhat_ky.jsonl`: nhật ký hoạt động nối thêm (append-only, không đưa lên Git).
  - `data/viec_chua_hoan_thanh.jsonl`: lưu trữ nối thêm bản đầy đủ các công việc bị hủy hoặc đánh dấu Chưa hoàn thành (append-only, không đưa lên Git).

API cần kết nối Internet. Mọi luồng API có timeout và hiển thị lỗi khi nguồn không khả dụng; dữ liệu dự án vẫn dùng được ngoại tuyến.
