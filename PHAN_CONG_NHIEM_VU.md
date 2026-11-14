# Bảng phân công nhiệm vụ đồ án Kanban

## Mục tiêu chung

Hoàn thiện ứng dụng quản lý quy trình Kanban bằng Python và Tkinter, lưu dữ liệu chính bằng JSON. Nhóm ưu tiên hoàn thành các chức năng bắt buộc và tích hợp ổn định trước; phần sáng tạo nâng cao thực hiện sau.

Nhóm đã xin phép giảng viên về quy mô 4 thành viên.

## Phân công theo thành viên

| Thành viên | Vai trò | Phần code chính | Công việc cụ thể | Bàn giao/tiêu chí hoàn thành |
|---|---|---|---|---|
| **Quốc** | Backend, OOP và điều phối tích hợp | `models/CongViec/`, `models/DuAn.py`, `services/QuanLyKaban.py`, `config.py`, `main.py` | Hoàn thiện model công việc thường/khẩn và dự án; CRUD công việc, chuyển trạng thái, tìm kiếm/lọc; kiểm tra quyền trong nghiệp vụ; thống nhất API public cho UI; kết nối các service và xử lý lỗi tích hợp; cấu hình hằng số và điểm khởi chạy | Model và service dùng API thống nhất; UI gọi được hàm public; nghiệp vụ không tự đọc/ghi file; ứng dụng khởi chạy qua `main.py` |
| **Huy** | Giao diện Tkinter | `ui/login_window.py`, `ui/main_window.py`, `ui/task_card.py`; có thể thêm `ui/task_form.py`, `ui/report_window.py` | Làm đăng nhập/đăng ký; cửa sổ Kanban theo cột; form tạo/sửa; tìm kiếm/lọc; chuyển trạng thái; xác nhận xóa/thoát; thông báo lỗi bằng `messagebox`; hiển thị thống kê bằng Canvas; chỉ gọi API service, không truy cập JSON trực tiếp | Giao diện có tối thiểu 6 loại widget, Treeview/Listbox và Custom Widget; layout đúng quy định; các luồng chính nối được với backend |
| **Khoa** | Lưu trữ JSON và xác thực tài khoản | `services/BoLuuTru/`, `models/NguoiDung/` hoặc `models/ThanhVien.py`, dữ liệu JSON mẫu | Đọc/ghi/backup JSON bằng `with`; xử lý file thiếu, rỗng, sai định dạng và lỗi truy cập; tạo tài khoản, đăng nhập/đăng xuất, đổi mật khẩu, vai trò; băm mật khẩu; ghi nhật ký trạng thái; thống nhất schema JSON với Quốc | API lưu trữ/xác thực được tài liệu hóa; dữ liệu tài khoản và dự án có thể tạo lại; mật khẩu không lưu dạng rõ; backup và nhật ký hoạt động được kiểm tra |
| **Phú** | Thống kê, API, kiểm thử tự động và báo cáo | `services/thong_ke.py`, `services/quote_api.py`, `tests/` hoặc `test_oop.py`, `TESTCASES.md`, `BAOCAO/` | Viết module thống kê hoàn thành/quá hạn và tổng hợp; gọi API/Crawl, xử lý timeout/lỗi và lưu dữ liệu JSON; viết test tự động cho API `QuanLyKanban`, JSON và thống kê; chạy kiểm thử tích hợp; phối hợp Huy nối thống kê/API vào UI; ghi kết quả test, làm báo cáo và slide | Module thống kê/API có interface rõ; tối thiểu 10 test gồm hợp lệ, sai và biên; bảng test có input/mong đợi/thực tế/trạng thái; báo cáo và slide khớp sản phẩm đã chạy |

## Phân chia kiểm thử và tích hợp

| Hạng mục | Người chính | Người phối hợp |
|---|---|---|
| API model và nghiệp vụ | Quốc | Phú viết test; Huy xác nhận UI cần gọi gì |
| Đọc/ghi/backup JSON và tài khoản | Khoa | Quốc thống nhất schema; Phú kiểm thử ca file lỗi |
| Giao diện và luồng thao tác | Huy | Quốc cung cấp API; Khoa xác nhận luồng tài khoản; Phú tích hợp phần thống kê |
| Thống kê và API/Crawl | Phú | Huy hiển thị trên giao diện; Quốc hỗ trợ tích hợp service |
| Kiểm thử hồi quy toàn ứng dụng | Phú điều phối | Cả nhóm sửa lỗi theo module phụ trách |
| Khởi chạy và ghép ứng dụng | Quốc | Huy, Khoa, Phú bàn giao module và xác nhận tích hợp |

## Các điểm nhóm phải thống nhất trước khi ghép

1. **API backend:** tên hàm, tham số, kiểu trả về và cách báo lỗi; Quốc gửi cho Huy và Phú trước khi họ nối module.
2. **Schema JSON:** tên file, khóa dữ liệu, kiểu dữ liệu và phiên bản schema; Khoa chốt cùng Quốc.
3. **Phiên đăng nhập và quyền:** cách truyền người dùng hiện tại; quyền admin và thành viên; Quốc/Khoa/Huy thống nhất.
4. **Nhãn và mức ưu tiên:** hai trường riêng; nhãn dùng phân loại, mức ưu tiên thể hiện độ gấp.
5. **API/Crawl:** quy định đồ án có đoạn yêu cầu bắt buộc và đoạn ghi chú khuyến khích; nhóm triển khai một API/Crawl để đáp ứng yêu cầu rõ nhất, đồng thời ghi nguồn.
6. **Chuyển cột:** đề tài cho phép kéo thả hoặc chuyển bằng thao tác chọn; nhóm cần bảo đảm chuyển trạng thái bằng UI hoạt động ổn định.

## Thứ tự triển khai

1. Khoa chốt schema JSON và dữ liệu mẫu; Quốc chốt API model/service.
2. Quốc bàn giao API sớm; Huy dựng giao diện và nối các luồng CRUD.
3. Khoa hoàn tất lưu trữ/xác thực; các module tích hợp vào điểm khởi chạy.
4. Phú hoàn thành thống kê/API, viết và chạy test trong lúc tích hợp; phối hợp Huy hiển thị kết quả.
5. Cả nhóm chạy hồi quy, sửa lỗi, hoàn thiện README/báo cáo/slide và đóng gói.

## Tiêu chí hoàn thành toàn nhóm

- Ứng dụng chạy được từ `main.py` theo hướng dẫn.
- Có CRUD, tìm kiếm/lọc, phân quyền và lưu/đọc JSON.
- File JSON thiếu/rỗng/sai định dạng được xử lý; có backup dữ liệu.
- Có giao diện Tkinter, thông báo/xác nhận thao tác quan trọng và thống kê trực quan.
- Có ít nhất một API/Crawl, xử lý lỗi kết nối và lưu kết quả vào JSON.
- Có ít nhất 10 test case và bảng ghi kết quả thực tế.
- Có dữ liệu mẫu, hướng dẫn cài đặt/chạy, báo cáo, slide và gói chạy thử.
- Mỗi thành viên hiểu và giải thích được phần mình phụ trách.
