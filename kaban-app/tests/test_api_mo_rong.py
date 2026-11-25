import unittest
from datetime import date
from unittest.mock import patch

from services.api_mo_rong import (cong_ngay_lam_viec, lay_ngay_le_viet_nam,
                                  lay_cau_dong_vien, lay_nguoi_dung_mau)


class TestApiMoRong(unittest.TestCase):
    def test_bo_qua_cuoi_tuan_va_ngay_le(self):
        self.assertEqual(cong_ngay_lam_viec(date(2026, 1, 1), 1, {date(2026, 1, 2)}),
                         date(2026, 1, 5))

    @patch("services.api_mo_rong.lay_du_lieu_api")
    def test_ngay_le(self, api):
        api.return_value = ({"holidays": [{"date": "2026-01-01"}]}, None)
        self.assertEqual(lay_ngay_le_viet_nam(2026)[0], {date(2026, 1, 1)})

    @patch("services.api_mo_rong.lay_du_lieu_api")
    def test_quote(self, api):
        api.return_value = ({"quote": "Keep going", "author": "A"}, None)
        self.assertEqual(lay_cau_dong_vien()[0]["noi_dung"], "Keep going")

    @patch("services.api_mo_rong.lay_du_lieu_api")
    def test_users(self, api):
        api.return_value = ([{"id": 1, "name": "Alice", "email": "alice@example.org"}], None)
        self.assertEqual(lay_nguoi_dung_mau()[0][0]["ten_dang_nhap"], "demo_1")


if __name__ == "__main__":
    unittest.main()
