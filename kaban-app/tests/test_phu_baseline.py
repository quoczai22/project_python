"""Các ca mẫu để Phú tiếp tục mở rộng cho thống kê và API."""

import io
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import URLError

from services.quote_api import lay_du_lieu_api, lay_va_luu_du_lieu_api
from services.thong_ke import thong_ke_du_an


def du_an_mau(*cong_viec):
    return SimpleNamespace(danh_sach_cot=["Cần làm", "Đang làm", "Hoàn thành"], cong_viec=list(cong_viec))


def viec(trang_thai, han, nguoi="phu"):
    return SimpleNamespace(trang_thai=trang_thai, ngay_ket_thuc=han, nguoi_phu_trach=nguoi)


class TestThongKe(unittest.TestCase):
    def setUp(self):
        self.hom_nay = date(2026, 11, 15)

    def test_du_an_rong(self):
        ket_qua = thong_ke_du_an(du_an_mau(), self.hom_nay)
        self.assertEqual((ket_qua["tong"], ket_qua["ty_le_hoan_thanh"]), (0, 0.0))

    def test_dem_trang_thai_va_thanh_vien(self):
        ket_qua = thong_ke_du_an(du_an_mau(viec("Cần làm", "2026-11-20"), viec("Hoàn thành", "2026-11-14", "quoc")), self.hom_nay)
        self.assertEqual(ket_qua["theo_trang_thai"]["Hoàn thành"], 1)
        self.assertEqual(ket_qua["theo_thanh_vien"], {"phu": 1, "quoc": 1})

    def test_ty_le_hoan_thanh(self):
        ket_qua = thong_ke_du_an(du_an_mau(viec("Cần làm", "2026-11-20"), viec("Hoàn thành", "2026-11-14")), self.hom_nay)
        self.assertEqual(ket_qua["ty_le_hoan_thanh"], 50.0)

    def test_viec_chua_xong_qua_han(self):
        ket_qua = thong_ke_du_an(du_an_mau(viec("Đang làm", "2026-11-14")), self.hom_nay)
        self.assertEqual(ket_qua["qua_han"], 1)

    def test_hoan_thanh_khong_tinh_qua_han(self):
        ket_qua = thong_ke_du_an(du_an_mau(viec("Hoàn thành", "2026-11-14")), self.hom_nay)
        self.assertEqual(ket_qua["qua_han"], 0)

    def test_han_hom_nay_khong_qua_han(self):
        ket_qua = thong_ke_du_an(du_an_mau(viec("Cần làm", "2026-11-15")), self.hom_nay)
        self.assertEqual(ket_qua["qua_han"], 0)


class TestApi(unittest.TestCase):
    def test_url_sai(self):
        self.assertIsNotNone(lay_du_lieu_api("example.com")[1])

    def test_timeout_sai(self):
        self.assertIsNotNone(lay_du_lieu_api("https://example.com", 0)[1])

    @patch("services.quote_api.urlopen")
    def test_json_hop_le(self, mo_urlopen):
        mo_urlopen.return_value.__enter__.return_value = io.BytesIO(b'{"content": "hello"}')
        self.assertEqual(lay_du_lieu_api("https://example.com")[0], {"content": "hello"})

    @patch("services.quote_api.urlopen", side_effect=URLError("offline"))
    def test_mat_mang(self, _mo_urlopen):
        self.assertIsNotNone(lay_du_lieu_api("https://example.com")[1])

    @patch("services.quote_api.urlopen")
    def test_luu_qua_tang_luu_tru(self, mo_urlopen):
        mo_urlopen.return_value.__enter__.return_value = io.BytesIO(b'{"content": "hello"}')
        luu_tru = SimpleNamespace(ghi_json=lambda duong_dan, du_lieu: True)
        self.assertEqual(lay_va_luu_du_lieu_api("https://example.com", "data/api.json", luu_tru)[1], None)


if __name__ == "__main__":
    unittest.main()
