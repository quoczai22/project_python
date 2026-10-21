import unittest
from datetime import datetime, timedelta
from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
from services.QuanLyKaban import QuanLyKanban, BoLuuTruBase, BoLuuTruMock
from models.CongViec import CongViec, CongViecThuong, CongViecKhan
from models.ThanhVien import NguoiDung, ThanhVien, QuanTriVien
from models.DuAn import DuAn
from exceptions import (
    KanbanException,
    DuLieuKhongHopLeError,
    KhongTimThayError,
    KhongCoQuyenError,
    XungDotDuLieuError,
    XacThucThatBaiError,
    LoiLuuTruError
)


class TestOOPVaXuLyLoiKanban(unittest.TestCase):

    def setUp(self):
        self.ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)
        self.hom_nay = datetime.now().date()
        self.hom_qua = (self.hom_nay - timedelta(days=1)).strftime("%Y-%m-%d")
        self.hai_ngay_toi = (self.hom_nay + timedelta(days=2)).strftime("%Y-%m-%d")
        self.hai_muoi_ngay_toi = (self.hom_nay + timedelta(days=20)).strftime("%Y-%m-%d")

    # ==================== 1. TÍNH TRỪU TƯỢNG (ABSTRACTION) ====================
    def test_truu_tuong_khong_the_khoi_tao_abstract_class(self):
        """Không thể khởi tạo trực tiếp các lớp trừu tượng (Abstract Base Classes)."""
        from typing import Any

        # Kiểm tra danh sách phương thức trừu tượng tồn tại theo chuẩn abc.ABC
        self.assertTrue(bool(CongViec.__abstractmethods__))
        self.assertTrue(bool(NguoiDung.__abstractmethods__))
        self.assertTrue(bool(BoLuuTruBase.__abstractmethods__))

        # Sử dụng ép kiểu Any để linter không báo cảnh báo tĩnh bad-instantiation
        # đồng thời vẫn đảm bảo kiểm thử chính xác TypeError tại runtime
        with self.assertRaises(TypeError):
            cls_cong_viec: Any = CongViec
            cls_cong_viec("CV-999", "Test", "Mo ta", "admin", "2026-10-01", "2026-10-10", "Cần làm", "Cao", "Backend")

        with self.assertRaises(TypeError):
            cls_nguoi_dung: Any = NguoiDung
            cls_nguoi_dung("user_test", "123456")

        with self.assertRaises(TypeError):
            cls_bo_luu_tru: Any = BoLuuTruBase
            cls_bo_luu_tru()

    # ==================== 2. TÍNH KẾ THỪA (INHERITANCE) ====================
    def test_ke_thua(self):
        """Quan hệ kế thừa giữa các lớp Model và Service."""
        cv_thuong = CongViecThuong("CV-101", "Việc thường", "Mô tả", "quoc", self.hom_nay.strftime("%Y-%m-%d"), self.hai_muoi_ngay_toi)
        cv_khan = CongViecKhan("CV-102", "Việc khẩn", "Mô tả", "admin", self.hom_nay.strftime("%Y-%m-%d"), self.hai_ngay_toi)

        self.assertIsInstance(cv_thuong, CongViec)
        self.assertIsInstance(cv_khan, CongViec)

        tv = ThanhVien("quoc", "123456")
        admin = QuanTriVien("admin", "123456")
        self.assertIsInstance(tv, NguoiDung)
        self.assertIsInstance(admin, NguoiDung)

        mock_storage = BoLuuTruMock()
        self.assertIsInstance(mock_storage, BoLuuTruBase)

    # ==================== 3. TÍNH ĐÓNG GÓI (ENCAPSULATION) ====================
    def test_dong_goi_va_validation(self):
        """Thuộc tính được bảo vệ, kiểm soát validation nghiêm ngặt và ném DuLieuKhongHopLeError."""
        cv = CongViecThuong("CV-101", "Việc thường", "Mô tả", "quoc", self.hom_nay.strftime("%Y-%m-%d"), self.hai_muoi_ngay_toi)

        # Thuộc tính có biến nội bộ _ma_cong_viec
        self.assertTrue(hasattr(cv, "_ma_cong_viec"))
        self.assertEqual(cv.ma_cong_viec, "CV-101")

        # Gán mã sai định dạng -> Ném DuLieuKhongHopLeError
        with self.assertRaises(DuLieuKhongHopLeError):
            cv.ma_cong_viec = "SAI_FORMAT"

        # Gán ngày kết thúc trước ngày bắt đầu -> Ném DuLieuKhongHopLeError
        with self.assertRaises(DuLieuKhongHopLeError):
            cv.ngay_ket_thuc = self.hom_qua

        # CongViecKhan bảo vệ mức ưu tiên luôn là 'Khẩn'
        cv_khan = CongViecKhan("CV-102", "Việc khẩn", "Mô tả", "admin", self.hom_nay.strftime("%Y-%m-%d"), self.hai_ngay_toi)
        with self.assertRaises(DuLieuKhongHopLeError):
            cv_khan.muc_uu_tien = "Thấp"
        self.assertEqual(cv_khan.muc_uu_tien, "Khẩn")

    # ==================== 4. TÍNH ĐA HÌNH (POLYMORPHISM) ====================
    def test_da_hinh_cong_viec(self):
        """Đa hình: Cùng gọi canh_bao() nhưng mỗi đối tượng phản hồi theo cấp độ riêng."""
        cv_thuong = CongViecThuong("CV-101", "Việc thường", "Mô tả", "quoc", self.hom_nay.strftime("%Y-%m-%d"), self.hai_muoi_ngay_toi)
        cv_khan = CongViecKhan("CV-102", "Việc khẩn", "Mô tả", "admin", self.hom_nay.strftime("%Y-%m-%d"), self.hai_ngay_toi)

        danh_sach = [cv_thuong, cv_khan]
        canh_bao_list = [cv.canh_bao() for cv in danh_sach]
        self.assertEqual(len(canh_bao_list), 2)
        self.assertIn("Còn", canh_bao_list[0])
        self.assertEqual("CẢNH BÁO ĐỎ - SẮP ĐẾN HẠN", canh_bao_list[1])

    def test_da_hinh_phan_quyen(self):
        """Đa hình: QuanTriVien có toàn quyền, ThanhVien bị giới hạn quyền."""
        du_an = DuAn("DA-999", "Dự án bảo mật", thanh_vien_tham_gia=["quoc"])
        admin = QuanTriVien("admin", "123456")
        member = ThanhVien("quoc", "123456")
        stranger = ThanhVien("huy", "123456")

        self.assertTrue(admin.kiem_tra_quyen_du_an(du_an))
        self.assertTrue(member.kiem_tra_quyen_du_an(du_an))
        self.assertFalse(stranger.kiem_tra_quyen_du_an(du_an))

        self.assertTrue(admin.co_quyen_xoa_cong_viec())
        self.assertFalse(member.co_quyen_xoa_cong_viec())

    # ==================== 5. XỬ LÝ LỖI BACKEND CHUẨN (ERROR HANDLING) ====================
    def test_ngoai_le_xac_thuc_dang_nhap(self):
        """Xử lý lỗi khi đăng nhập: Sai mật khẩu hoặc tài khoản không tồn tại."""
        # Tài khoản không tồn tại
        with self.assertRaises(KhongTimThayError):
            self.ql.dang_nhap("user_khong_ton_tai", "123456")

        # Sai mật khẩu
        with self.assertRaises(XacThucThatBaiError):
            self.ql.dang_nhap("admin", "sai_mat_khau")

    def test_ngoai_le_xung_dot_du_lieu(self):
        """Ném XungDotDuLieuError khi tạo trùng mã dự án hoặc công việc."""
        du_an = DuAn("DA-999", "Dự án mới")
        cv = CongViecThuong("CV-101", "Việc 1", "Mo ta", "admin", self.hom_nay.strftime("%Y-%m-%d"), self.hai_muoi_ngay_toi)
        du_an.them_cong_viec(cv)

        # Thêm công việc trùng mã vào dự án
        with self.assertRaises(XungDotDuLieuError):
            cv_trung = CongViecThuong("CV-101", "Việc trùng", "Mo ta", "admin", self.hom_nay.strftime("%Y-%m-%d"), self.hai_muoi_ngay_toi)
            du_an.them_cong_viec(cv_trung)

    def test_ngoai_le_khong_co_quyen(self):
        """Ném KhongCoQuyenError khi người dùng không đủ quyền thực hiện hành động."""
        du_an = DuAn("DA-999", "Dự án Test", thanh_vien_tham_gia=["quoc"])
        cv = CongViecThuong("CV-101", "Việc 1", "Mo ta", "quoc", self.hom_nay.strftime("%Y-%m-%d"), self.hai_muoi_ngay_toi)
        du_an.them_cong_viec(cv)

        # Người dùng 'huy' chưa thuộc dự án
        self.ql.nguoi_dung_hien_tai = ThanhVien("huy", "123456")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.tao_cong_viec(du_an, {"MaCongViec": "CV-105", "TieuDe": "Test", "NguoiPhuTrach": "huy", "NgayBatDau": self.hom_nay.strftime("%Y-%m-%d"), "NgayKetThuc": self.hai_ngay_toi})

        # Thành viên thường không có quyền xóa công việc
        self.ql.nguoi_dung_hien_tai = ThanhVien("quoc", "123456")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.xoa_cong_viec(du_an, "CV-101")

    def test_co_che_rollback_khi_luu_loi(self):
        """Kiểm tra tính toàn vẹn dữ liệu: Rollback trạng thái khi tầng lưu trữ gặp sự cố."""
        class BoLuuTruLoi(BoLuuTruMock):
            def ghi_json(self, ten_file, du_lieu):
                raise OSError("Mô phỏng lỗi đĩa hoặc mạng!")

        ql_loi = QuanLyKanban(BoLuuTruLoi())
        ql_loi.nguoi_dung_hien_tai = QuanTriVien("admin", "123456")
        du_an = DuAn("DA-888", "Dự án Rollback", thanh_vien_tham_gia=["admin"])
        ql_loi.danh_sach_du_an.append(du_an)

        so_luong_ban_dau = len(du_an.danh_sach_cong_viec)

        # Khi tạo công việc bị lỗi ghi đĩa -> phải Rollback, danh sách không bị rác
        with self.assertRaises(LoiLuuTruError):
            ql_loi.tao_cong_viec(du_an, {
                "MaCongViec": "CV-888",
                "TieuDe": "Việc thử rollback",
                "NguoiPhuTrach": "admin",
                "NgayBatDau": self.hom_nay.strftime("%Y-%m-%d"),
                "NgayKetThuc": self.hai_muoi_ngay_toi
            })

        # Đảm bảo danh sách công việc đã được rollback về đúng số lượng ban đầu
        self.assertEqual(len(du_an.danh_sach_cong_viec), so_luong_ban_dau)
        self.assertIsNone(du_an.tim_cong_viec_theo_ma("CV-888"))

    def test_quan_ly_binh_luan(self):
        """Kiểm tra tạo, thêm và xóa bình luận trên công việc Kanban."""
        from models.BinhLuan import BinhLuan
        du_an = DuAn("DA-999", "Dự án Bình Luận", thanh_vien_tham_gia=["quoc"])
        cv = CongViecThuong("CV-101", "Việc có bình luận", "Mô tả", "quoc", self.hom_nay.strftime("%Y-%m-%d"), self.hai_muoi_ngay_toi)
        du_an.them_cong_viec(cv)

        # Đăng nhập để bình luận
        self.ql.nguoi_dung_hien_tai = ThanhVien("quoc", "123456")
        bl = self.ql.them_binh_luan_cong_viec(du_an, "CV-101", "Đang tiến hành xử lý phần backend")
        self.assertEqual(len(cv.danh_sach_binh_luan), 1)
        self.assertEqual(cv.danh_sach_binh_luan[0].noi_dung, "Đang tiến hành xử lý phần backend")

        # Xóa bình luận
        self.ql.xoa_binh_luan_cong_viec(du_an, "CV-101", bl.ma_binh_luan)
        self.assertEqual(len(cv.danh_sach_binh_luan), 0)



if __name__ == "__main__":
    unittest.main()
