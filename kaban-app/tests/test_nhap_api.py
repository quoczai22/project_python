"""Kiểm thử chức năng nhập công việc từ API (DummyJSON Todos).

Chạy:  python -m unittest tests.test_nhap_api -v
Mọi test dùng thư mục tạm và giả lập (mock) mạng, không gọi API thật, không đụng dữ liệu thật.
"""
import io
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from services.QuanLyKaban import QuanLyKanban
from services.nhap_api import lam_sach_todos, lay_todos_tu_api, nhap_cong_viec_tu_api

DU_LIEU_API = {
    "todos": [
        {"id": 1, "todo": "Do something nice", "completed": True, "userId": 26},
        {"id": 2, "todo": "  Learn   Python  ", "completed": False, "userId": 7},
        {"id": 3, "todo": "Build a Kanban app", "completed": False, "userId": 5},
    ],
    "total": 150, "skip": 0, "limit": 3,
}


def gia_lap_api(du_lieu):
    """Tạo mock cho urlopen trả về `du_lieu` dưới dạng JSON."""
    return patch("services.quote_api.urlopen", **{
        "return_value.__enter__.return_value": io.BytesIO(json.dumps(du_lieu).encode("utf-8"))
    })


class TestLamSach(unittest.TestCase):
    def test_hop_le(self):
        kq = lam_sach_todos(DU_LIEU_API)
        self.assertEqual([m["id"] for m in kq], [1, 2, 3])
        self.assertTrue(kq[0]["hoan_thanh"])
        self.assertEqual(kq[1]["tieu_de"], "Learn Python")          # bỏ khoảng trắng thừa

    def test_sai_cau_truc(self):
        for xau in (None, [], {"data": []}, {"todos": "abc"}):
            with self.assertRaises(ValueError):
                lam_sach_todos(xau)

    def test_bo_ban_ghi_loi_va_trung(self):
        du_lieu = {"todos": [
            {"id": 1, "todo": "A"}, {"id": 1, "todo": "Trùng id"}, {"id": "2", "todo": "id sai kiểu"},
            {"id": 3, "todo": "   "}, {"id": 4}, "rác", {"id": True, "todo": "bool"}, {"id": 5, "todo": "B"},
        ]}
        self.assertEqual([m["id"] for m in lam_sach_todos(du_lieu)], [1, 5])

    def test_cat_tieu_de_dai_va_gioi_han_so_luong(self):
        du_lieu = {"todos": [{"id": i, "todo": "x" * 500} for i in range(1, 20)]}
        kq = lam_sach_todos(du_lieu, 4)
        self.assertEqual(len(kq), 4)
        self.assertEqual(len(kq[0]["tieu_de"]), 80)


class CoSo(unittest.TestCase):
    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.ql = QuanLyKanban(os.path.join(self.thu_muc, "du_an.json"),
                               os.path.join(self.thu_muc, "du_lieu_moc.json"))
        self.ql.dang_nhap("admin", "123456")
        self.du_an = self.ql.tao_du_an("DA-001", "Dự án thử")
        # trỏ file lưu dữ liệu API vào thư mục tạm
        self.f_api = os.path.join(self.thu_muc, "api_todos.json")
        p = patch("services.nhap_api.TEN_FILE_API", self.f_api)
        p.start(); self.addCleanup(p.stop)

    def tearDown(self):
        shutil.rmtree(self.thu_muc, ignore_errors=True)


class TestNhapApi(CoSo):
    def test_nhap_thanh_cong_va_luu_json(self):
        with gia_lap_api(DU_LIEU_API):
            kq = nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        self.assertEqual((kq["them"], kq["trung"], kq["loi"], kq["thong_bao"]), (3, 0, 0, None))
        self.assertEqual(len(self.du_an.cong_viec), 3)
        trang_thai = {cv.tieu_de: cv.trang_thai for cv in self.du_an.cong_viec}
        self.assertEqual(trang_thai["Do something nice"], "Hoàn thành")
        self.assertEqual(trang_thai["Learn Python"], "Cần làm")
        with open(self.f_api, encoding="utf-8") as f:
            da_luu = json.load(f)
        self.assertEqual(len(da_luu["todos"]), 3)
        self.assertIn("dummyjson.com", da_luu["nguon"])

    def test_nhap_lan_hai_khong_trung(self):
        with gia_lap_api(DU_LIEU_API):
            nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        with gia_lap_api(DU_LIEU_API):
            kq = nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        self.assertEqual((kq["them"], kq["trung"]), (0, 3))
        self.assertEqual(len(self.du_an.cong_viec), 3)

    def test_mat_mang_khong_lam_hong_ung_dung(self):
        with patch("services.quote_api.urlopen", side_effect=URLError("offline")):
            kq = nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        self.assertIn("Không kết nối được API", kq["thong_bao"])
        self.assertEqual(len(self.du_an.cong_viec), 0)
        self.assertFalse(os.path.exists(self.f_api))

    def test_het_thoi_gian_cho(self):
        with patch("services.quote_api.urlopen", side_effect=TimeoutError("timed out")):
            _, loi = lay_todos_tu_api(3, self.ql.bo_luu_tru)
        self.assertIsNotNone(loi)

    def test_api_tra_json_sai_cau_truc(self):
        with gia_lap_api({"message": "Server error"}):
            kq = nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        self.assertIn("sai cấu trúc", kq["thong_bao"])
        self.assertEqual(len(self.du_an.cong_viec), 0)

    def test_api_tra_danh_sach_rong(self):
        with gia_lap_api({"todos": [], "total": 0}):
            kq = nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        self.assertIn("không trả về công việc hợp lệ", kq["thong_bao"])

    def test_phan_hoi_khong_phai_json(self):
        with patch("services.quote_api.urlopen") as mo:
            mo.return_value.__enter__.return_value = io.BytesIO(b"<html>502 Bad Gateway</html>")
            kq = nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        self.assertIsNotNone(kq["thong_bao"])

    def test_ma_cong_viec_khong_trung_voi_viec_co_san(self):
        with gia_lap_api(DU_LIEU_API):
            nhap_cong_viec_tu_api(self.ql, self.du_an, 3)
        ma = [cv.ma_cong_viec for cv in self.du_an.cong_viec]
        self.assertEqual(len(ma), len(set(ma)))
        self.assertEqual(ma, ["CV-001", "CV-002", "CV-003"])

    def test_url_co_limit_va_skip(self):
        with gia_lap_api(DU_LIEU_API) as mo:
            lay_todos_tu_api(3, self.ql.bo_luu_tru, skip=40)
        yeu_cau = mo.call_args[0][0]
        self.assertIn("limit=3", yeu_cau.full_url)
        self.assertIn("skip=40", yeu_cau.full_url)


if __name__ == "__main__":
    unittest.main()