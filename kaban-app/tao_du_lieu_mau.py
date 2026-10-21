"""Tạo dữ liệu mẫu để test giao diện (CHỈ DÙNG TRÊN MÁY MÌNH, KHÔNG COMMIT)."""
import json
import os
from datetime import date, timedelta

from models.NguoiDung.NguoiDungBase import bam_mat_khau  # mật khẩu mẫu cũng được băm SHA-256

THU_MUC = os.path.dirname(os.path.abspath(__file__))


def ngay(so_ngay):
    """Trả về ngày 'hôm nay + so_ngay' dạng YYYY-MM-DD."""
    return (date.today() + timedelta(days=so_ngay)).strftime("%Y-%m-%d")


def cong_viec(ma, tieu_de, nguoi, trang_thai, uu_tien, nhan, bat_dau, ket_thuc, mo_ta=""):
    return {
        "LoaiCongViec": "CongViecKhan" if uu_tien == "Khẩn" else "CongViecThuong",
        "MaCongViec": ma,
        "TieuDe": tieu_de,
        "MoTa": mo_ta,
        "NguoiPhuTrach": nguoi,
        "NgayBatDau": ngay(bat_dau),
        "NgayKetThuc": ngay(ket_thuc),
        "TrangThai": trang_thai,
        "MucUuTien": uu_tien,
        "Nhan": nhan,
        "DanhSachBinhLuan": [],
    }


THANH_VIEN = {
    "thanh_vien": [
        {"ten_dang_nhap": "admin", "mat_khau": bam_mat_khau("123456"), "ho_ten": "Quản trị viên Hệ thống", "email": "admin@kanban.vn", "vai_tro": "quan_tri"},
        {"ten_dang_nhap": "quoc", "mat_khau": bam_mat_khau("123456"), "ho_ten": "Trịnh Quốc", "email": "quoc@kanban.vn", "vai_tro": "thanh_vien"},
        {"ten_dang_nhap": "khoa", "mat_khau": bam_mat_khau("123456"), "ho_ten": "Đăng Khoa", "email": "khoa@kanban.vn", "vai_tro": "thanh_vien"},
        {"ten_dang_nhap": "huy", "mat_khau": bam_mat_khau("123456"), "ho_ten": "Gia Huy", "email": "huy@kanban.vn", "vai_tro": "thanh_vien"},
        {"ten_dang_nhap": "phu", "mat_khau": bam_mat_khau("123456"), "ho_ten": "Hồng Phú", "email": "phu@kanban.vn", "vai_tro": "thanh_vien"},
    ]
}

DU_AN = [
    {
        "MaDuAn": "DA-001",
        "TenDuAn": "Ứng dụng Quản lý Kanban",
        "DanhSachCot": ["Cần làm", "Đang làm", "Kiểm tra", "Hoàn thành"],
        "ThanhVienThamGia": ["quoc", "khoa", "huy", "phu"],
        "NgayTao": ngay(-14),
        "DanhSachCongViec": [
            cong_viec("CV-001", "Viết model CongViec", "quoc", "Hoàn thành", "Cao", "Backend", -14, -7),
            cong_viec("CV-002", "Viết lớp BoLuuTru đọc/ghi JSON", "khoa", "Hoàn thành", "Cao", "Backend", -13, -6),
            cong_viec("CV-003", "Dựng cửa sổ đăng nhập", "huy", "Kiểm tra", "Trung bình", "Giao diện", -7, 2),
            cong_viec("CV-004", "Dựng bảng Kanban theo cột", "huy", "Đang làm", "Cao", "Giao diện", -5, 5,
                      "Mỗi cột là một Frame, mỗi thẻ là một TaskCard."),
            cong_viec("CV-005", "Sửa lỗi mất dữ liệu khi lưu", "khoa", "Đang làm", "Khẩn", "Lỗi", -2, 1),
            cong_viec("CV-006", "Viết unit test cho rollback", "quoc", "Cần làm", "Trung bình", "Kiểm thử", 0, 10),
            cong_viec("CV-007", "Viết báo cáo đồ án", "phu", "Cần làm", "Thấp", "Tài liệu", 0, 20),
            cong_viec("CV-008", "Chuẩn bị slide thuyết trình", "phu", "Cần làm", "Thấp", "Tài liệu", -10, -1,
                      "Việc này cố ý để quá hạn để xem thẻ báo đỏ."),
        ],
    },
    {
        "MaDuAn": "DA-002",
        "TenDuAn": "Website giới thiệu lớp",
        "DanhSachCot": ["Cần làm", "Đang làm", "Kiểm tra", "Hoàn thành"],
        "ThanhVienThamGia": ["huy", "phu"],
        "NgayTao": ngay(-3),
        "DanhSachCongViec": [
            cong_viec("CV-001", "Thiết kế trang chủ", "huy", "Cần làm", "Trung bình", "Giao diện", 0, 7),
            cong_viec("CV-002", "Viết nội dung giới thiệu", "phu", "Đang làm", "Thấp", "Tài liệu", -1, 6),
        ],
    },
]


def ghi_neu_chua_co(ten_file, du_lieu):
    duong_dan = os.path.join(THU_MUC, ten_file)
    if os.path.exists(duong_dan):
        print(f"[BỎ QUA] {ten_file} đã có sẵn, không ghi đè.")
        return
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2)
    print(f"[OK] Đã tạo {ten_file}")


if __name__ == "__main__":
    ghi_neu_chua_co("du_lieu_moc.json", THANH_VIEN)
    ghi_neu_chua_co("du_an.json", DU_AN)