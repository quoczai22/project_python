"""Bộ kiểm thử bổ sung cho nhiệm vụ thống kê, API, JSON và facade QuanLyKanban."""
import csv
import io
import json
import os
import tempfile
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from services.QuanLyKaban import QuanLyKanban
from services.quote_api import lay_du_lieu_api, lay_va_luu_du_lieu_api
from services.thong_ke import thong_ke_du_an, xuat_bao_cao_file


def cv(trang_thai="Cần làm", han="2026-11-20", nguoi="phu", ma="CV-001", tieu_de="Việc mẫu"):
    return SimpleNamespace(
        trang_thai=trang_thai, ngay_ket_thuc=han, nguoi_phu_trach=nguoi,
        ma_cong_viec=ma, tieu_de=tieu_de, muc_uu_tien="Trung bình",
        ngay_bat_dau="2026-11-01", canh_bao=lambda: "Không có cảnh báo", can_chu_y=lambda: False,
    )


def du_an(*ds):
    return SimpleNamespace(ma_du_an="DA-TEST", ten_du_an="Dự án kiểm thử",
                           danh_sach_cot=["Cần làm", "Đang làm", "Kiểm tra", "Hoàn thành"],
                           cong_viec=list(ds))


class TestThongKeNangCao(unittest.TestCase):
    hom_nay = date(2026, 11, 15)

    def test_dem_tong_va_chua_hoan_thanh(self):
        kq = thong_ke_du_an(du_an(cv(), cv("Hoàn thành")), self.hom_nay)
        self.assertEqual((kq["tong"], kq["chua_hoan_thanh"], kq["hoan_thanh"]), (2, 1, 1))

    def test_ti_le_chua_hoan_thanh(self):
        kq = thong_ke_du_an(du_an(cv(), cv("Hoàn thành")), self.hom_nay)
        self.assertEqual(kq["ty_le_chua_hoan_thanh"], 50.0)

    def test_ngay_qua_han(self):
        self.assertEqual(thong_ke_du_an(du_an(cv(han="2026-11-14")), self.hom_nay)["qua_han"], 1)

    def test_ngay_hom_nay_khong_qua_han(self):
        self.assertEqual(thong_ke_du_an(du_an(cv(han="2026-11-15")), self.hom_nay)["qua_han"], 0)

    def test_cong_viec_hoan_thanh_khong_tinh_qua_han(self):
        self.assertEqual(thong_ke_du_an(du_an(cv("Hoàn thành", "2020-01-01")), self.hom_nay)["qua_han"], 0)

    def test_ngay_thieu_khong_lam_vo_thong_ke(self):
        kq = thong_ke_du_an(du_an(cv(han=None)), self.hom_nay)
        self.assertEqual(kq["ngay_khong_hop_le"], 1)
        self.assertEqual(kq["tong"], 1)

    def test_ngay_sai_dinh_dang_khong_lam_vo_thong_ke(self):
        self.assertEqual(thong_ke_du_an(du_an(cv(han="31/11/2026")), self.hom_nay)["ngay_khong_hop_le"], 1)

    def test_chua_phan_cong_duoc_nhom_rieng(self):
        self.assertEqual(thong_ke_du_an(du_an(cv(nguoi="")), self.hom_nay)["theo_thanh_vien"], {"Chưa phân công": 1})

    def test_trang_thai_la_moi_van_duoc_dem(self):
        kq = thong_ke_du_an(du_an(cv("Tạm dừng")), self.hom_nay)
        self.assertEqual(kq["theo_trang_thai"]["Tạm dừng"], 1)

    def test_bao_cao_csv_co_cac_chi_so_moi(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "report.csv")
            xuat_bao_cao_file(du_an(cv()), path)
            with open(path, encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("Chưa hoàn thành", content)
            self.assertIn("Ngày hạn không hợp lệ", content)

    def test_bao_cao_txt_co_chi_tiet(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "report.txt")
            xuat_bao_cao_file(du_an(cv()), path)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Dự án kiểm thử", content)
            self.assertIn("Việc mẫu", content)


class TestApiVaJson(unittest.TestCase):
    def test_tu_choi_url_khong_hop_le(self):
        self.assertIsNone(lay_du_lieu_api("ftp://example.com")[0])

    def test_tu_choi_timeout_khong_duong(self):
        self.assertIsNotNone(lay_du_lieu_api("https://example.com", 0)[1])

    @patch("services.quote_api.urlopen")
    def test_doc_json_thanh_cong(self, mo):
        mo.return_value.__enter__.return_value = io.BytesIO(b'{"ok": true}')
        self.assertEqual(lay_du_lieu_api("https://example.com")[0], {"ok": True})

    @patch("services.quote_api.urlopen", side_effect=URLError("offline"))
    def test_loi_mang_duoc_bao_ve(self, _):
        self.assertIn("offline", lay_du_lieu_api("https://example.com")[1])

    @patch("services.quote_api.urlopen", side_effect=TimeoutError("timeout"))
    def test_timeout_duoc_bao_ve(self, _):
        self.assertIn("timeout", lay_du_lieu_api("https://example.com")[1])

    @patch("services.quote_api.urlopen", side_effect=HTTPError("https://example.com", 500, "server", {}, None))
    def test_http_500_duoc_bao_ve(self, _):
        self.assertIsNotNone(lay_du_lieu_api("https://example.com")[1])

    @patch("services.quote_api.urlopen")
    def test_json_hong_duoc_bao_ve(self, mo):
        mo.return_value.__enter__.return_value = io.BytesIO(b"not-json")
        self.assertIsNotNone(lay_du_lieu_api("https://example.com")[1])

    @patch("services.quote_api.urlopen")
    def test_luu_json_qua_storage(self, mo):
        mo.return_value.__enter__.return_value = io.BytesIO(b'{"items": [1]}')
        luu = SimpleNamespace(ghi_json=lambda path, data: True)
        data, error = lay_va_luu_du_lieu_api("https://example.com", "api.json", luu)
        self.assertEqual(data, {"items": [1]})
        self.assertIsNone(error)

    @patch("services.quote_api.urlopen")
    def test_bao_loi_neu_storage_that_bai(self, mo):
        mo.return_value.__enter__.return_value = io.BytesIO(b'{"items": [1]}')
        luu = SimpleNamespace(ghi_json=lambda path, data: False)
        self.assertIn("Không lưu được", lay_va_luu_du_lieu_api("https://example.com", "api.json", luu)[1])


class TestTichHopQuanLyKanban(unittest.TestCase):
    def test_facade_khoi_tao_va_lay_danh_sach_du_an(self):
        with tempfile.TemporaryDirectory() as td:
            ql = QuanLyKanban(os.path.join(td, "projects.json"), os.path.join(td, "users.json"))
            self.assertIsInstance(ql.lay_danh_sach_du_an(), list)

    def test_admin_dang_nhap_va_tao_du_an(self):
        with tempfile.TemporaryDirectory() as td:
            ql = QuanLyKanban(os.path.join(td, "projects.json"), os.path.join(td, "users.json"))
            self.assertTrue(ql.dang_nhap("admin", "123456"))
            da = ql.tao_du_an("DA-999", "Dự án tích hợp")
            self.assertEqual(da.ma_du_an, "DA-999")


if __name__ == "__main__":
    unittest.main()
