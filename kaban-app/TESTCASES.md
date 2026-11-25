# TESTCASES – Kiểm thử phần việc của Phú

**Phạm vi:** `services/thong_ke.py`, `services/quote_api.py`, API nhập Todos, tầng JSON và facade `QuanLyKanban`.

**Cách chạy:**

```bash
cd kaban-app
python -m unittest discover tests -v
```

Các ca kiểm thử API đều giả lập phản hồi mạng bằng `unittest.mock`; không phụ thuộc Internet và không ghi đè dữ liệu thật.

## Bảng test case trọng tâm

| ID | Nhóm | Đầu vào / thao tác | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
|---|---|---|---|---|---|
| TK01 | Thống kê | Dự án không có công việc | Tổng = 0, tỷ lệ hoàn thành = 0% | Đúng | PASS |
| TK02 | Thống kê | 1 việc hoàn thành, 1 việc cần làm | Tổng 2; hoàn thành 1; chưa hoàn thành 1 | Đúng | PASS |
| TK03 | Thống kê | Hạn trước ngày hiện tại, trạng thái chưa xong | Tăng số việc quá hạn | Đúng | PASS |
| TK04 | Thống kê | Hạn đúng ngày hiện tại | Không tính quá hạn | Đúng | PASS |
| TK05 | Thống kê | Việc hoàn thành có hạn trong quá khứ | Không tính quá hạn | Đúng | PASS |
| TK06 | Thống kê | Ngày kết thúc bị thiếu | Không làm crash; tăng ngày không hợp lệ | Đúng | PASS |
| TK07 | Thống kê | Ngày kết thúc sai định dạng | Không làm crash; tăng ngày không hợp lệ | Đúng | PASS |
| TK08 | Thống kê | Người phụ trách rỗng | Gom vào nhóm Chưa phân công | Đúng | PASS |
| TK09 | Báo cáo | Xuất CSV | Có tổng quan, chưa hoàn thành, hạn không hợp lệ | Đúng | PASS |
| TK10 | Báo cáo | Xuất TXT | Có tên dự án và chi tiết công việc | Đúng | PASS |
| API01 | API | URL không dùng HTTP/HTTPS | Trả thông báo lỗi | Đúng | PASS |
| API02 | API | Timeout bằng 0 | Trả thông báo lỗi | Đúng | PASS |
| API03 | API | API trả JSON hợp lệ | Đọc được dữ liệu JSON | Đúng | PASS |
| API04 | API | Mất mạng | Bắt lỗi, không làm dừng ứng dụng | Đúng | PASS |
| API05 | API | Timeout khi gọi API | Bắt lỗi timeout | Đúng | PASS |
| API06 | API | Máy chủ trả HTTP 500 | Bắt lỗi HTTP | Đúng | PASS |
| API07 | API | Phản hồi không phải JSON | Bắt lỗi giải mã | Đúng | PASS |
| API08 | JSON | Ghi dữ liệu qua tầng lưu trữ | Gọi `ghi_json` với dữ liệu nhận được | Đúng | PASS |
| API09 | JSON | Tầng lưu trữ từ chối ghi | Trả thông báo không lưu được | Đúng | PASS |
| INT01 | Tích hợp | Khởi tạo `QuanLyKanban` với file tạm | Facade hoạt động, trả danh sách dự án | Đúng | PASS |
| INT02 | Tích hợp | Admin đăng nhập và tạo dự án đúng định dạng | Tạo được dự án và trả đúng mã | Đúng | PASS |

## Kết quả chạy tự động

- Bộ kiểm thử hiện có trên main: 86 test.
- Bộ kiểm thử bổ sung của Phú: 22 test.
- Tổng: **108 test – PASS 108 – FAIL 0**.
- Thời gian chạy lần kiểm tra ghi nhận: khoảng 1,5 giây.
- Lệnh: `python -m unittest discover tests`.

> Ghi chú: Đây là kết quả kiểm thử tự động trong môi trường phát triển. Giao diện Tkinter và kết nối API thật cần được chạy thử trên máy trình diễn để xác nhận thao tác trực quan và tình trạng mạng tại thời điểm demo.

