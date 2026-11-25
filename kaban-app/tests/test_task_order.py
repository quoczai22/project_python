"""Kiểm tra thứ tự kéo thả và hoàn tác khi không lưu được."""

import unittest
from types import SimpleNamespace

from exceptions import LoiLuuTruError
from ui.components.task_order import chen_cong_viec


def viec(ten, cot="Cần làm"):
    return SimpleNamespace(ten=ten, trang_thai=cot)


class TestTaskOrder(unittest.TestCase):
    def setUp(self):
        self.a, self.b, self.c = viec("A"), viec("B"), viec("C")
        self.du_an = SimpleNamespace(danh_sach_cong_viec=[self.a, self.b, self.c])

    def test_keo_xuong_tru_mot_vi_tri_cua_the_dang_keo(self):
        chen_cong_viec(self.du_an, self.a, "Cần làm", 2, lambda: None, cung_cot=True)
        self.assertEqual([cv.ten for cv in self.du_an.danh_sach_cong_viec], ["B", "A", "C"])

    def test_keo_len_khong_tru_vi_tri(self):
        chen_cong_viec(self.du_an, self.c, "Cần làm", 0, lambda: None, cung_cot=True)
        self.assertEqual([cv.ten for cv in self.du_an.danh_sach_cong_viec], ["C", "A", "B"])

    def test_chuyen_cot_giu_vi_tri_tha(self):
        self.a.trang_thai = "Đang làm"
        self.du_an.danh_sach_cong_viec.append(viec("D", "Đang làm"))
        chen_cong_viec(self.du_an, self.a, "Đang làm", 0, lambda: None)
        self.assertEqual([cv.ten for cv in self.du_an.danh_sach_cong_viec if cv.trang_thai == "Đang làm"], ["A", "D"])

    def test_luu_loi_khoi_phuc_danh_sach_va_bao_loi(self):
        def luu_loi():
            raise OSError("disk full")

        with self.assertRaises(LoiLuuTruError):
            chen_cong_viec(self.du_an, self.a, "Cần làm", 2, luu_loi, cung_cot=True)
        self.assertEqual([cv.ten for cv in self.du_an.danh_sach_cong_viec], ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
