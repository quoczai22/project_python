"""
Kiểm thử phần Khoa: lưu trữ JSON (đọc/ghi/sao lưu/khôi phục), tài khoản (băm SHA-256, đăng ký, đăng nhập), nhật ký.
Chạy:  python -m unittest test_luu_tru_tai_khoan -v
Mọi test chạy trong thư mục tạm, không đụng tới dữ liệu thật của ứng dụng.
"""
import json
import os
import shutil
import tempfile
import unittest

from services.QuanLyKaban import QuanLyKanban
from services.BoLuuTru import BoLuuTruMock
from models.ThanhVien import ThanhVien, QuanTriVien, NguoiDung
from models.NguoiDung.NguoiDungBase import bam_mat_khau, la_mat_khau_da_bam
from exceptions import (
    DuLieuKhongHopLeError, XungDotDuLieuError, XacThucThatBaiError,
    KhongTimThayError, LoiLuuTruError
)


class CoSoTest(unittest.TestCase):
    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.f_da = os.path.join(self.thu_muc, "du_an.json")
        self.f_tk = os.path.join(self.thu_muc, "du_lieu_moc.json")
        self.f_nk = os.path.join(self.thu_muc, "nhat_ky.json")
        self.bo = BoLuuTruMock(self.f_da, self.f_tk)
        self.bo.ten_file_nhat_ky = self.f_nk

    def tearDown(self):
        shutil.rmtree(self.thu_muc, ignore_errors=True)

    def viet(self, duong_dan, noi_dung, che_do="w"):
        with open(duong_dan, che_do, **({} if "b" in che_do else {"encoding": "utf-8"})) as f:
            f.write(noi_dung)

    def doc(self, duong_dan):
        with open(duong_dan, "r", encoding="utf-8") as f:
            return f.read()


class TestBamMatKhau(unittest.TestCase):
    def test_luu_dang_bam_khong_luu_mat_khau_tho(self):
        tv = ThanhVien("khoa", "matkhau123")
        d = tv.to_dict()
        self.assertNotIn("matkhau123", d["mat_khau"])
        self.assertTrue(la_mat_khau_da_bam(d["mat_khau"]))

    def test_cung_mat_khau_khac_salt_khac_ban_bam(self):
        self.assertNotEqual(bam_mat_khau("abcdef"), bam_mat_khau("abcdef"))

    def test_kiem_tra_dung_sai(self):
        tv = QuanTriVien("admin", "123456")
        self.assertTrue(tv.kiem_tra_mat_khau("123456"))
        self.assertFalse(tv.kiem_tra_mat_khau("654321"))
        self.assertFalse(tv.kiem_tra_mat_khau(""))

    def test_to_dict_from_dict_khong_bam_lai(self):
        tv = ThanhVien("khoa", "123456")
        d = tv.to_dict()
        tv2 = NguoiDung.from_dict(d)
        self.assertEqual(tv2.to_dict()["mat_khau"], d["mat_khau"])
        self.assertTrue(tv2.kiem_tra_mat_khau("123456"))

    def test_from_dict_mat_khau_tho_duoc_bam(self):
        tv = NguoiDung.from_dict({"ten_dang_nhap": "cu", "mat_khau": "123456"})
        self.assertTrue(la_mat_khau_da_bam(tv.to_dict()["mat_khau"]))
        self.assertTrue(tv.kiem_tra_mat_khau("123456"))

    def test_from_dict_thieu_mat_khau(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            NguoiDung.from_dict({"ten_dang_nhap": "x"})

    def test_doi_mat_khau(self):
        tv = ThanhVien("khoa", "123456")
        tv.doi_mat_khau("123456", "abcdef")
        self.assertTrue(tv.kiem_tra_mat_khau("abcdef"))
        self.assertFalse(tv.kiem_tra_mat_khau("123456"))
        self.assertTrue(la_mat_khau_da_bam(tv.to_dict()["mat_khau"]))


class TestDocGhiVaFileLoi(CoSoTest):
    def test_ghi_roi_doc_lai(self):
        self.bo.ghi_json(self.f_da, [{"a": "tiếng Việt"}])
        self.assertEqual(self.bo.doc_json(self.f_da), [{"a": "tiếng Việt"}])
        self.assertFalse(os.path.exists(self.f_da + ".tmp"))

    def test_file_khong_ton_tai(self):
        with self.assertRaises(LoiLuuTruError):
            self.bo.doc_json(self.f_da)

    def test_file_rong_khong_co_backup(self):
        self.viet(self.f_da, "")
        with self.assertRaises(LoiLuuTruError) as ctx:
            self.bo.doc_json(self.f_da)
        self.assertIn("rỗng", ctx.exception.thong_diep)

    def test_file_chi_co_khoang_trang(self):
        self.viet(self.f_da, "  \n\n ")
        with self.assertRaises(LoiLuuTruError):
            self.bo.doc_json(self.f_da)

    def test_file_sai_cu_phap(self):
        self.viet(self.f_da, "{hong")
        with self.assertRaises(LoiLuuTruError) as ctx:
            self.bo.doc_json(self.f_da)
        self.assertIn("cú pháp", ctx.exception.thong_diep)

    def test_file_sai_dinh_dang_kieu(self):
        self.viet(self.f_da, '"chi la chuoi"')
        with self.assertRaises(LoiLuuTruError) as ctx:
            self.bo.doc_json(self.f_da)
        self.assertIn("sai định dạng", ctx.exception.thong_diep)

    def test_file_co_bom_van_doc_duoc(self):
        self.viet(self.f_da, b"\xef\xbb\xbf[1, 2]", "wb")
        self.assertEqual(self.bo.doc_json(self.f_da), [1, 2])

    def test_file_sai_ma_hoa(self):
        self.viet(self.f_da, b"\xff\xfe\x00[", "wb")
        with self.assertRaises(LoiLuuTruError):
            self.bo.doc_json(self.f_da)

    def test_ghi_du_lieu_khong_serialize_duoc_khong_dong_den_file(self):
        self.bo.ghi_json(self.f_da, [1])
        with self.assertRaises(LoiLuuTruError):
            self.bo.ghi_json(self.f_da, [object()])
        self.assertEqual(self.bo.doc_json(self.f_da), [1])


class TestSaoLuuVaKhoiPhuc(CoSoTest):
    def test_ghi_de_tao_ban_sao_luu_ban_cu(self):
        self.bo.ghi_json(self.f_da, ["v1"])
        self.assertEqual(self.bo.danh_sach_sao_luu(self.f_da), [])   # lần đầu chưa có gì để sao lưu
        self.bo.ghi_json(self.f_da, ["v2"])
        cac_ban = self.bo.danh_sach_sao_luu(self.f_da)
        self.assertEqual(len(cac_ban), 1)
        self.assertEqual(json.loads(self.doc(cac_ban[0])), ["v1"])

    def test_gioi_han_so_ban_sao_luu(self):
        for i in range(25):
            self.bo.ghi_json(self.f_da, [i])
        self.assertLessEqual(len(self.bo.danh_sach_sao_luu(self.f_da)), 10)

    def test_khong_tao_ban_sao_luu_trung(self):
        self.bo.ghi_json(self.f_da, ["a"])
        self.bo.sao_luu(self.f_da)
        self.bo.sao_luu(self.f_da)
        self.assertEqual(len(self.bo.danh_sach_sao_luu(self.f_da)), 1)

    def test_khoi_phuc_khi_file_hong(self):
        self.bo.ghi_json(self.f_da, ["tot"])
        self.bo.ghi_json(self.f_da, ["tot", "moi"])
        self.viet(self.f_da, "{hong")
        self.assertEqual(self.bo.doc_json(self.f_da), ["tot"])           # lấy từ backup
        self.assertEqual(json.loads(self.doc(self.f_da)), ["tot"])       # file gốc đã được sửa lại
        thu_muc_bk = os.path.join(self.thu_muc, "backup")
        self.assertTrue(any(".loi-" in t for t in os.listdir(thu_muc_bk)))  # bản hỏng được giữ lại

    def test_khoi_phuc_khi_file_rong(self):
        self.bo.ghi_json(self.f_da, ["tot"])
        self.bo.ghi_json(self.f_da, ["tot2"])
        self.viet(self.f_da, "")
        self.assertEqual(self.bo.doc_json(self.f_da), ["tot"])

    def test_khoi_phuc_khi_sai_kieu(self):
        self.bo.ghi_json(self.f_da, ["tot"])
        self.bo.ghi_json(self.f_da, ["tot2"])
        self.viet(self.f_da, '{"khong": "phai list"}')
        self.assertEqual(self.bo.doc_json(self.f_da), ["tot"])

    def test_file_hong_khong_lam_mat_ban_sao_luu_tot(self):
        self.bo.ghi_json(self.f_da, ["tot"])
        self.bo.ghi_json(self.f_da, ["tot2"])
        so_ban = len(self.bo.danh_sach_sao_luu(self.f_da))
        self.viet(self.f_da, "{hong")
        for _ in range(15):                      # ghi đè liên tục khi file đang hỏng
            self.viet(self.f_da, "{hong")
            self.bo.sao_luu(self.f_da)
        self.assertEqual(len(self.bo.danh_sach_sao_luu(self.f_da)), so_ban)

    def test_ghi_de_len_file_hong_van_giu_ban_hong(self):
        self.viet(self.f_da, "{noi dung quan trong nhung hong")
        self.bo.ghi_json(self.f_da, [])
        thu_muc_bk = os.path.join(self.thu_muc, "backup")
        bans = [t for t in os.listdir(thu_muc_bk) if ".loi-" in t]
        self.assertEqual(len(bans), 1)
        self.assertIn("noi dung quan trong", self.doc(os.path.join(thu_muc_bk, bans[0])))


class TestNhatKy(CoSoTest):
    def test_ghi_nhieu_ban_ghi_va_doc_lai(self):
        for i, (cu, moi) in enumerate([("Cần làm", "Đang làm"), ("Đang làm", "Hoàn thành")]):
            self.assertTrue(self.bo.ghi_nhat_ky({
                "ten_dang_nhap": "khoa", "ma_cong_viec": f"CV-00{i}",
                "trang_thai_cu": cu, "trang_thai_moi": moi}))
        nk = self.bo.doc_nhat_ky()
        self.assertEqual(len(nk), 2)
        self.assertEqual(nk[1]["trang_thai_cu"], "Đang làm")
        self.assertIn("thoi_gian", nk[0])

    def test_chua_co_file_doc_ra_rong(self):
        self.assertEqual(self.bo.doc_nhat_ky(), [])

    def test_nhat_ky_hong_khong_mat_du_lieu_cu(self):
        self.bo.ghi_nhat_ky({"ten_dang_nhap": "a", "ma_cong_viec": "CV-1"})
        self.bo.ghi_nhat_ky({"ten_dang_nhap": "b", "ma_cong_viec": "CV-2"})
        self.viet(self.f_nk, "[{hong")
        self.bo.ghi_nhat_ky({"ten_dang_nhap": "c", "ma_cong_viec": "CV-3"})
        # File hỏng được khôi phục từ bản sao lưu gần nhất (trước bản ghi 'b'), rồi ghi tiếp 'c'.
        ten = [m["ten_dang_nhap"] for m in self.bo.doc_nhat_ky()]
        self.assertEqual(ten, ["a", "c"])

    def test_nhat_ky_hong_khong_co_backup_van_giu_ban_hong(self):
        self.viet(self.f_nk, "[{hong")
        self.assertTrue(self.bo.ghi_nhat_ky({"ten_dang_nhap": "c"}))
        self.assertEqual(len(self.bo.doc_nhat_ky()), 1)
        thu_muc_bk = os.path.join(self.thu_muc, "backup")
        self.assertTrue(any(".loi-" in t for t in os.listdir(thu_muc_bk)))

    def test_ban_ghi_khong_phai_dict(self):
        self.assertFalse(self.bo.ghi_nhat_ky("khong hop le"))

    def test_khong_ghi_de_khi_loi_doc_io(self):
        self.bo.ghi_nhat_ky({"ten_dang_nhap": "a"})
        goc = self.bo.doc_json

        def loi_io(ten_file):
            raise LoiLuuTruError("Lỗi khi đọc file giả lập")
        self.bo.doc_json = loi_io
        self.assertFalse(self.bo.ghi_nhat_ky({"ten_dang_nhap": "b"}))
        self.bo.doc_json = goc
        self.assertEqual(len(self.bo.doc_nhat_ky()), 1)


class TestTaiKhoan(CoSoTest):
    def setUp(self):
        super().setUp()
        self.ql = QuanLyKanban(self.bo)

    def test_chua_co_file_tu_tao_du_lieu_mau_1_quan_tri_1_thanh_vien(self):
        ds = self.bo.doc_danh_sach_thanh_vien()
        vai_tro = sorted(nd.vai_tro for nd in ds)
        self.assertEqual(vai_tro, ["quan_tri", "thanh_vien"])
        self.assertTrue(os.path.exists(self.f_tk))
        self.assertNotIn('"123456"', self.doc(self.f_tk))      # trong file không có mật khẩu thô

    def test_dang_nhap_tai_khoan_mau(self):
        nd = self.ql.dang_nhap("admin", "123456")
        self.assertEqual(nd.vai_tro, "quan_tri")

    def test_dang_nhap_sai(self):
        self.bo.doc_danh_sach_thanh_vien()
        with self.assertRaises(XacThucThatBaiError):
            self.ql.dang_nhap("admin", "sai")
        with self.assertRaises(KhongTimThayError):
            self.ql.dang_nhap("khong_co", "123456")

    def test_dang_ky_thanh_cong_va_dang_nhap_duoc(self):
        tv = self.ql.dang_ky("huy_01", "matkhau1", "Nguyễn Huy", "huy@gmail.com")
        self.assertEqual(tv.vai_tro, "thanh_vien")
        self.assertEqual(self.ql.dang_nhap("huy_01", "matkhau1").ten_dang_nhap, "huy_01")
        self.assertNotIn("matkhau1", self.doc(self.f_tk))
        self.assertEqual(len(self.ql.lay_danh_sach_nguoi_dung()), 3)

    def test_dang_ky_trung_ten_khong_phan_biet_hoa_thuong(self):
        self.ql.dang_ky("huy01", "matkhau1")
        with self.assertRaises(XungDotDuLieuError):
            self.ql.dang_ky("HUY01", "matkhau2")
        with self.assertRaises(XungDotDuLieuError):
            self.ql.dang_ky("admin", "matkhau2")

    def test_dang_ky_trung_email(self):
        self.ql.dang_ky("a_user", "matkhau1", "", "x@gmail.com")
        with self.assertRaises(XungDotDuLieuError):
            self.ql.dang_ky("b_user", "matkhau1", "", "X@Gmail.com")

    def test_dang_ky_email_sai(self):
        for email in ("abc", "a@b", "a@@b.com", "a b@c.com", "@c.com", "a@.com", "a@b.c"):
            with self.subTest(email=email):
                with self.assertRaises(DuLieuKhongHopLeError):
                    self.ql.dang_ky("user_ok", "matkhau1", "", email)

    def test_dang_ky_email_dung(self):
        for i, email in enumerate(("a@gmail.com", "ten.ho+tag@sv.edu.vn", "x_y-z@mail.co")):
            self.ql.dang_ky(f"user_{i}", "matkhau1", "", email)

    def test_dang_ky_email_de_trong_duoc_phep(self):
        self.ql.dang_ky("khong_email", "matkhau1", "Tên", "")

    def test_dang_ky_ten_khong_hop_le(self):
        for ten in ("", "ab", "a" * 21, "có dấu", "co khoang", "a-b", "a@b"):
            with self.subTest(ten=ten):
                with self.assertRaises(DuLieuKhongHopLeError):
                    self.ql.dang_ky(ten, "matkhau1")

    def test_dang_ky_mat_khau_ngan(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.dang_ky("user_ok", "12345")

    def test_dang_ky_that_bai_khong_ghi_gi(self):
        self.bo.doc_danh_sach_thanh_vien()
        truoc = self.doc(self.f_tk)
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.dang_ky("user_ok", "1")
        self.assertEqual(self.doc(self.f_tk), truoc)

    def test_dang_ky_loi_luu_tru(self):
        self.bo.doc_danh_sach_thanh_vien()

        def loi_ghi(*a, **k):
            raise LoiLuuTruError("giả lập hết dung lượng")
        self.bo.ghi_danh_sach_thanh_vien = loi_ghi
        with self.assertRaises(LoiLuuTruError):
            self.ql.dang_ky("user_ok", "matkhau1")
        del self.bo.ghi_danh_sach_thanh_vien
        with self.assertRaises(KhongTimThayError):
            self.ql.dang_nhap("user_ok", "matkhau1")

    def test_khong_the_tu_dang_ky_quan_tri(self):
        tv = self.ql.dang_ky("hacker", "matkhau1", "Hacker", "h@x.com")
        self.assertEqual(tv.vai_tro, "thanh_vien")
        self.assertFalse(tv.co_quyen_xoa_cong_viec())

    def test_chuyen_mat_khau_tho_cu_sang_bam(self):
        self.viet(self.f_tk, json.dumps({"thanh_vien": [
            {"ten_dang_nhap": "cu", "mat_khau": "123456", "vai_tro": "quan_tri"}]}))
        self.assertEqual(self.ql.dang_nhap("cu", "123456").vai_tro, "quan_tri")
        self.assertNotIn('"123456"', self.doc(self.f_tk))
        self.assertTrue(la_mat_khau_da_bam(json.loads(self.doc(self.f_tk))["thanh_vien"][0]["mat_khau"]))
        self.assertEqual(self.ql.dang_nhap("cu", "123456").ten_dang_nhap, "cu")  # vẫn đăng nhập được sau khi băm

    def test_ban_ghi_tai_khoan_loi_khong_lam_hong_nguoi_khac(self):
        self.viet(self.f_tk, json.dumps({"thanh_vien": [
            {"ten_dang_nhap": "", "mat_khau": "123456"},
            {"ten_dang_nhap": "thieu_mk"},
            "rac",
            {"ten_dang_nhap": "tot", "mat_khau": "123456"}]}))
        self.assertEqual(self.ql.dang_nhap("tot", "123456").ten_dang_nhap, "tot")

    def test_file_tai_khoan_hong_khoi_phuc_tu_backup(self):
        self.ql.dang_ky("user_ok", "matkhau1")
        self.ql.dang_ky("user_ok2", "matkhau1")
        self.viet(self.f_tk, "{hong")
        self.assertEqual(self.ql.dang_nhap("user_ok", "matkhau1").ten_dang_nhap, "user_ok")

    def test_file_tai_khoan_hong_khong_co_backup_tao_lai_mau(self):
        self.viet(self.f_tk, "")
        self.assertEqual(self.ql.dang_nhap("admin", "123456").vai_tro, "quan_tri")


if __name__ == "__main__":
    unittest.main()
