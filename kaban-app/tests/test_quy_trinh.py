import os
import tempfile
import unittest
from datetime import date, timedelta

from services.QuanLyKaban import QuanLyKanban
from exceptions import DuLieuKhongHopLeError, KhongCoQuyenError


class TestQuyTrinh(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ql = QuanLyKanban(os.path.join(self.tmp.name, "du_an.json"),
                               os.path.join(self.tmp.name, "users.json"))
        self.ql.bo_luu_tru.ten_file_nhat_ky = os.path.join(self.tmp.name, "nhat_ky.json")
        self.ql.dang_ky("lead", "123456", "Leader", "lead@test.vn")
        self.ql.dang_ky("worker", "123456", "Worker", "worker@test.vn")
        self.ql.dang_nhap("admin", "123456")
        self.da = self.ql.tao_du_an("DA-999", "Dự án kiểm thử")
        self.ql.them_thanh_vien_du_an(self.da, "lead")
        self.ql.them_thanh_vien_du_an(self.da, "worker")
        self.ql.cap_quyen_truong_nhom(self.da, "lead")
        self.ql.gan_thanh_vien_nhom(self.da, "lead", "worker")

    def tao(self, ma="CV-001", nguoi="worker", han=None):
        hom_nay = date.today()
        return self.ql.tao_cong_viec(self.da, {
            "ma_cong_viec": ma, "tieu_de": "Việc thử", "nguoi_phu_trach": nguoi,
            "ngay_bat_dau": (hom_nay-timedelta(days=10)).isoformat(),
            "ngay_ket_thuc": han or (hom_nay-timedelta(days=1)).isoformat(),
            "trang_thai": "Cần làm", "muc_uu_tien": "Thấp", "nhan": "Backend"})

    def test_duyet_viec_va_nhom(self):
        self.ql.dang_nhap("worker", "123456")
        cv = self.tao()
        self.assertEqual(cv.trang_thai_duyet, "cho_duyet")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.chuyen_trang_thai(self.da, cv.ma_cong_viec, "Đang làm")
        self.ql.dang_nhap("lead", "123456")
        self.ql.duyet_cong_viec(self.da, cv.ma_cong_viec)
        self.assertEqual(cv.trang_thai_duyet, "da_duyet")

    def test_leader_can_admin_duyet(self):
        self.ql.dang_nhap("lead", "123456")
        cv = self.tao(nguoi="lead")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.duyet_cong_viec(self.da, cv.ma_cong_viec)
        self.ql.dang_nhap("admin", "123456")
        self.ql.duyet_cong_viec(self.da, cv.ma_cong_viec)

    def test_gia_han_toi_da_ba_lan(self):
        cv = self.tao()
        self.ql.dang_nhap("worker", "123456")
        self.ql.yeu_cau_gia_han(self.da, cv.ma_cong_viec,
                                (date.today()+timedelta(days=5)).isoformat(), "Cần thêm thời gian")
        self.ql.dang_nhap("lead", "123456")
        self.ql.duyet_gia_han(self.da, cv.ma_cong_viec)
        self.assertEqual(len(cv.lich_su_gia_han), 1)
        for lan in (2, 3):
            cv.ngay_ket_thuc = (date.today()-timedelta(days=1)).isoformat()
            self.ql.dang_nhap("worker", "123456")
            self.ql.yeu_cau_gia_han(self.da, cv.ma_cong_viec,
                                    (date.today()+timedelta(days=5+lan)).isoformat(), "Cần thêm thời gian")
            self.ql.dang_nhap("lead", "123456")
            self.ql.duyet_gia_han(self.da, cv.ma_cong_viec)
        self.assertEqual(len(cv.lich_su_gia_han), 3)
        cv.ngay_ket_thuc = (date.today()-timedelta(days=1)).isoformat()
        self.ql.dang_nhap("worker", "123456")
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.yeu_cau_gia_han(self.da, cv.ma_cong_viec,
                                    (date.today()+timedelta(days=20)).isoformat(), "Lần thứ tư")

    def test_huy_va_khoi_phuc_khong_mat_du_lieu(self):
        cv = self.tao()
        self.ql.huy_cong_viec(self.da, cv.ma_cong_viec, "Không còn cần")
        self.assertEqual(cv.trang_thai, "Đã hủy")
        self.assertIs(self.da.tim_cong_viec_theo_ma(cv.ma_cong_viec), cv)
        self.ql.khoi_phuc_cong_viec(self.da, cv.ma_cong_viec)
        self.assertEqual(cv.trang_thai, "Cần làm")

    def test_khong_go_thanh_vien_con_viec(self):
        self.tao()
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.xoa_thanh_vien_du_an(self.da, "worker")

    def test_go_thanh_vien_da_hoan_thanh_giu_lich_su(self):
        cv = self.tao()
        cv.trang_thai = "Hoàn thành"
        self.ql.xoa_thanh_vien_du_an(self.da, "worker")
        self.assertIn("worker", self.da.thanh_vien_da_roi)
        self.assertEqual(cv.nguoi_phu_trach, "worker")
        self.assertIn(cv, self.da.cong_viec)

    def test_mo_lai_can_leader_duyet(self):
        cv = self.tao()
        cv.trang_thai = "Hoàn thành"
        self.ql.dang_nhap("worker", "123456")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.chuyen_trang_thai(self.da, cv.ma_cong_viec, "Cần làm")
        self.ql.yeu_cau_mo_lai(self.da, cv.ma_cong_viec, "Cần sửa lại")
        self.ql.dang_nhap("lead", "123456")
        self.ql.duyet_mo_lai(self.da, cv.ma_cong_viec)
        self.assertEqual(cv.trang_thai, "Cần làm")

    def test_khoa_tai_khoan(self):
        self.ql.dat_khoa_tai_khoan("lead")
        self.ql.dang_xuat()
        from exceptions import XacThucThatBaiError
        with self.assertRaises(XacThucThatBaiError):
            self.ql.dang_nhap("lead", "123456")

    def test_leader_chi_them_go_thanh_vien_nhom_minh(self):
        self.ql.dang_ky("newbie", "123456", "New", "newbie@test.vn")
        self.ql.dang_nhap("lead", "123456")
        self.ql.them_thanh_vien_du_an(self.da, "newbie")
        self.assertIn("newbie", self.da.nhom["lead"])
        self.ql.xoa_thanh_vien_du_an(self.da, "newbie")
        self.assertIn("newbie", self.da.thanh_vien_da_roi)

    def test_viec_bi_tu_choi_duoc_gui_lai(self):
        self.ql.dang_nhap("worker", "123456")
        cv = self.tao()
        self.ql.dang_nhap("lead", "123456")
        self.ql.duyet_cong_viec(self.da, cv.ma_cong_viec, False)
        self.assertEqual(cv.trang_thai_duyet, "tu_choi")
        self.ql.dang_nhap("worker", "123456")
        self.ql.gui_lai_cong_viec(self.da, cv.ma_cong_viec)
        self.assertEqual(cv.trang_thai_duyet, "cho_duyet")

    def test_luu_lai_metadata_sau_khi_doc_json(self):
        cv = self.tao()
        self.ql.huy_cong_viec(self.da, cv.ma_cong_viec, "Lỗi yêu cầu")
        moi = QuanLyKanban(os.path.join(self.tmp.name, "du_an.json"),
                           os.path.join(self.tmp.name, "users.json"))
        da = moi.tim_du_an_theo_ma("DA-999")
        self.assertEqual(da.tim_cong_viec_theo_ma("CV-001").trang_thai, "Đã hủy")
        self.assertIn("lead", da.nhom)

    def test_audit_file_chi_noi_them(self):
        self.tao()
        audit = self.ql.bo_luu_tru.ten_file_nhat_ky + "l"
        self.assertTrue(os.path.exists(audit))
        with open(audit, encoding="utf-8") as f:
            before = f.read()
        self.ql.huy_cong_viec(self.da, "CV-001", "Lỗi yêu cầu")
        with open(audit, encoding="utf-8") as f:
            after = f.read()
        self.assertTrue(after.startswith(before))

    def test_chuyen_nhom_va_thu_hoi_leader(self):
        self.ql.dang_ky("lead2", "123456", "Leader 2", "lead2@test.vn")
        self.ql.them_thanh_vien_du_an(self.da, "lead2")
        self.ql.cap_quyen_truong_nhom(self.da, "lead2")
        self.ql.chuyen_thanh_vien_nhom(self.da, "worker", "lead2")
        self.assertNotIn("worker", self.da.nhom["lead"])
        self.assertIn("worker", self.da.nhom["lead2"])
        self.ql.thu_hoi_quyen_truong_nhom("lead")
        self.assertNotIn("lead", self.da.nhom)
        self.ql.chuyen_thanh_vien_nhom(self.da, "worker", None)
        self.assertNotIn("worker", self.da.nhom["lead2"])

    def test_leader_ban_giao_viec_trong_nhom_roi_go_thanh_vien(self):
        self.ql.dang_ky("worker2", "123456", "Worker 2", "worker2@test.vn")
        self.ql.them_thanh_vien_du_an(self.da, "worker2")
        self.ql.gan_thanh_vien_nhom(self.da, "lead", "worker2")
        cv = self.tao(nguoi="worker")
        self.ql.dang_nhap("lead", "123456")
        self.assertTrue(self.ql.kiem_tra_quyen_cong_viec(cv, du_an=self.da))
        self.ql.cap_nhat_cong_viec(self.da, cv.ma_cong_viec, {"nguoi_phu_trach": "worker2"})
        self.assertEqual(cv.nguoi_phu_trach, "worker2")
        self.ql.xoa_thanh_vien_du_an(self.da, "worker")
        self.assertIn("worker", self.da.thanh_vien_da_roi)

    def test_tu_choi_mo_lai_va_gia_han_cho_gui_lai(self):
        cv = self.tao()
        self.ql.dang_nhap("worker", "123456")
        han_moi = (date.today() + timedelta(days=5)).isoformat()
        self.ql.yeu_cau_gia_han(self.da, cv.ma_cong_viec, han_moi, "Cần thêm thời gian")
        self.ql.dang_nhap("lead", "123456")
        self.ql.duyet_gia_han(self.da, cv.ma_cong_viec, chap_nhan=False)
        self.assertIsNone(cv.yeu_cau_gia_han)
        self.assertEqual(len(cv.lich_su_gia_han), 0)
        self.ql.dang_nhap("worker", "123456")
        self.ql.yeu_cau_gia_han(self.da, cv.ma_cong_viec, han_moi, "Gửi lại gia hạn")
        self.assertIsNotNone(cv.yeu_cau_gia_han)

        cv.trang_thai = "Hoàn thành"
        self.ql.yeu_cau_mo_lai(self.da, cv.ma_cong_viec, "Cần kiểm tra lại")
        self.ql.dang_nhap("lead", "123456")
        self.ql.duyet_mo_lai(self.da, cv.ma_cong_viec, chap_nhan=False)
        self.assertIsNone(cv.yeu_cau_mo_lai)
        self.assertEqual(cv.trang_thai, "Hoàn thành")

    def test_khoi_phuc_don_sach_metadata_huy(self):
        cv = self.tao()
        self.ql.huy_cong_viec(self.da, cv.ma_cong_viec, "Hủy tạm")
        self.ql.khoi_phuc_cong_viec(self.da, cv.ma_cong_viec)
        self.assertEqual(cv.ly_do_huy, "")
        self.assertEqual(cv.nguoi_huy, "")
        self.assertEqual(cv.thoi_gian_huy, "")

    def test_duyet_hoan_thanh_cong_viec(self):
        cv = self.tao(nguoi="worker")
        self.ql.dang_nhap("worker", "123456")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.chuyen_trang_thai(self.da, cv.ma_cong_viec, "Hoàn thành")
        self.ql.chuyen_trang_thai(self.da, cv.ma_cong_viec, "Kiểm tra")
        self.assertEqual(cv.trang_thai, "Kiểm tra")

        # Leader từ chối không lý do bị chặn, có lý do -> về Đang làm
        self.ql.dang_nhap("lead", "123456")
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.duyet_hoan_thanh(self.da, cv.ma_cong_viec, chap_nhan=False, ly_do="   ")
        self.ql.duyet_hoan_thanh(self.da, cv.ma_cong_viec, chap_nhan=False, ly_do="Thiếu kiểm thử")
        self.assertEqual(cv.trang_thai, "Đang làm")
        self.assertEqual(cv.ly_do_tu_choi_hoan_thanh, "Thiếu kiểm thử")

        # Chuyển lại sang Kiểm tra -> Leader duyệt -> Hoàn thành (và ghi nhận trễ hạn)
        self.ql.dang_nhap("worker", "123456")
        self.ql.chuyen_trang_thai(self.da, cv.ma_cong_viec, "Kiểm tra")
        self.ql.dang_nhap("lead", "123456")
        self.ql.duyet_hoan_thanh(self.da, cv.ma_cong_viec, chap_nhan=True)
        self.assertEqual(cv.trang_thai, "Hoàn thành")
        self.assertTrue(cv.hoan_thanh_tre)

    def test_leader_khong_duyet_hoan_thanh_cua_minh_hoac_ngoai_nhom_va_admin_tu_duyet(self):
        self.ql.dang_ky("ngoai", "123456", "Ngoai", "ngoai@test.vn")
        self.ql.them_thanh_vien_du_an(self.da, "ngoai")
        cv_lead = self.tao(ma="CV-010", nguoi="lead")
        cv_ngoai = self.tao(ma="CV-011", nguoi="ngoai")
        cv_admin = self.tao(ma="CV-012", nguoi="admin")

        # Admin tự chuyển sang Hoàn thành được
        self.ql.chuyen_trang_thai(self.da, cv_admin.ma_cong_viec, "Hoàn thành")
        self.assertEqual(cv_admin.trang_thai, "Hoàn thành")

        # Leader không tự chuyển việc của mình sang Hoàn thành, không duyệt việc của mình / ngoài nhóm
        self.ql.dang_nhap("lead", "123456")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.chuyen_trang_thai(self.da, cv_lead.ma_cong_viec, "Hoàn thành")
        self.ql.chuyen_trang_thai(self.da, cv_lead.ma_cong_viec, "Kiểm tra")
        with self.assertRaises(KhongCoQuyenError):
            self.ql.duyet_hoan_thanh(self.da, cv_lead.ma_cong_viec)

        cv_ngoai.trang_thai = "Kiểm tra"
        with self.assertRaises(KhongCoQuyenError):
            self.ql.duyet_hoan_thanh(self.da, cv_ngoai.ma_cong_viec)

        # Admin duyệt được việc của Leader
        self.ql.dang_nhap("admin", "123456")
        self.ql.duyet_hoan_thanh(self.da, cv_lead.ma_cong_viec)
        self.assertEqual(cv_lead.trang_thai, "Hoàn thành")

    def test_khong_gia_han_viec_da_huy(self):
        cv = self.tao()  # hạn chót hôm qua -> quá hạn
        self.ql.huy_cong_viec(self.da, cv.ma_cong_viec, "Không còn cần")
        self.ql.dang_nhap("worker", "123456")
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.yeu_cau_gia_han(self.da, cv.ma_cong_viec,
                                    (date.today() + timedelta(days=5)).isoformat(), "Xin thêm thời gian")
        self.assertIsNone(cv.yeu_cau_gia_han)

    def test_khong_giao_viec_cho_nguoi_ngoai_du_an(self):
        self.ql.dang_ky("outsider", "123456", "Outsider", "outsider@test.vn")
        with self.assertRaises(DuLieuKhongHopLeError):
            self.tao(ma="CV-002", nguoi="outsider")
        with self.assertRaises(DuLieuKhongHopLeError):
            self.tao(ma="CV-003", nguoi="khong_ton_tai")
        cv = self.tao(ma="CV-004", nguoi="worker")
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.cap_nhat_cong_viec(self.da, cv.ma_cong_viec, {"nguoi_phu_trach": "outsider"})
        self.assertEqual(cv.nguoi_phu_trach, "worker")
        # Quản trị viên vẫn được nhận việc dù không nằm trong danh sách thành viên
        self.tao(ma="CV-005", nguoi="admin")

    def test_huy_viec_xoa_yeu_cau_dang_cho(self):
        cv = self.tao()
        self.ql.dang_nhap("worker", "123456")
        self.ql.yeu_cau_gia_han(self.da, cv.ma_cong_viec,
                                (date.today() + timedelta(days=5)).isoformat(), "Cần thêm thời gian")
        self.ql.dang_nhap("admin", "123456")
        self.ql.huy_cong_viec(self.da, cv.ma_cong_viec, "Không còn cần")
        self.ql.khoi_phuc_cong_viec(self.da, cv.ma_cong_viec)
        self.assertIsNone(cv.yeu_cau_gia_han)
        self.assertIsNone(cv.yeu_cau_mo_lai)
        with self.assertRaises(KhongCoQuyenError):
            self.ql.duyet_gia_han(self.da, cv.ma_cong_viec)


if __name__ == "__main__":
    unittest.main()
