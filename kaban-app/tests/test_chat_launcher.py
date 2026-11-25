"""Kiểm thử services.chat_launcher: chuẩn hóa địa chỉ, dò cổng, bật server bằng .bat, nối/ngắt client."""
import asyncio
import os
import socket
import tempfile
import threading
import time
import unittest
from types import SimpleNamespace
from unittest import mock

from services import chat_launcher as cl

try:
    import websockets  # noqa: F401
    CO_WEBSOCKETS = True
except ImportError:
    CO_WEBSOCKETS = False


def cong_trong() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestChuanHoaDiaChi(unittest.TestCase):
    def test_dang_hop_le(self):
        casos = {
            "192.168.100.232": "ws://192.168.100.232:8765",
            "  192.168.100.232  ": "ws://192.168.100.232:8765",
            "192.168.1.5:9000": "ws://192.168.1.5:9000",
            "ws://10.0.0.2:8765": "ws://10.0.0.2:8765",
            "ws://10.0.0.2": "ws://10.0.0.2:8765",
            "http://10.0.0.2/": "ws://10.0.0.2:8765",
            "may-chu.lan": "ws://may-chu.lan:8765",
        }
        for vao, ra in casos.items():
            self.assertEqual(cl.chuan_hoa_dia_chi(vao), ra, vao)

    def test_dang_khong_hop_le(self):
        for sai in ("", "   ", "192.168.1.5:abc", "192.168.1.5:0", "192.168.1.5:70000",
                    "192.168 1.5", "a b", "ws://", "-abc", "192.168.1.5:"):
            with self.assertRaises(ValueError, msg=repr(sai)):
                cl.chuan_hoa_dia_chi(sai)

    def test_tach_url(self):
        self.assertEqual(cl.tach_url("ws://1.2.3.4:9000"), ("1.2.3.4", 9000))


class TestDoCong(unittest.TestCase):
    def test_cong_dong_va_mo(self):
        cong = cong_trong()
        self.assertFalse(cl.cong_dang_mo("127.0.0.1", cong, cho=0.2))
        with socket.socket() as s:
            s.bind(("127.0.0.1", cong))
            s.listen(1)
            self.assertTrue(cl.cong_dang_mo("127.0.0.1", cong, cho=0.5))

    def test_lay_ip_lan_luon_tra_ve_chuoi_ipv4(self):
        ip = cl.lay_ip_lan()
        self.assertEqual(len(ip.split(".")), 4)


class TestBatMayChu(unittest.TestCase):
    def test_file_bat_ton_tai_va_dung_cong(self):
        self.assertTrue(os.path.isfile(cl.FILE_BAT))
        with open(cl.FILE_BAT, "rb") as f:
            noi_dung = f.read()
        self.assertIn(b"chat_server.py", noi_dung)
        self.assertIn(b"8765", noi_dung)
        self.assertIn(b"\r\n", noi_dung)          # .bat phải xuống dòng kiểu Windows
        noi_dung.decode("ascii")                   # tránh lỗi mã hóa tiếng Việt trong cmd

    def test_cong_da_mo_thi_khong_chay_bat_them(self):
        khoi_dong = mock.Mock()
        with mock.patch.object(cl, "cong_dang_mo", return_value=True):
            url = cl.bat_may_chu(khoi_dong=khoi_dong)
        self.assertEqual(url, "ws://127.0.0.1:8765")
        khoi_dong.assert_not_called()

    def test_cong_chua_mo_thi_chay_bat_va_cho(self):
        khoi_dong = mock.Mock()
        # lần 1: chưa mở (trước khi chạy .bat); sau đó: đã mở
        with mock.patch.object(cl, "cong_dang_mo", side_effect=[False, True]):
            url = cl.bat_may_chu(khoi_dong=khoi_dong, toi_da=2)
        khoi_dong.assert_called_once_with(cl.FILE_BAT)
        self.assertEqual(url, "ws://127.0.0.1:8765")

    def test_het_gio_cho_thi_bao_loi(self):
        with mock.patch.object(cl, "cong_dang_mo", return_value=False):
            with self.assertRaises(TimeoutError):
                cl.bat_may_chu(khoi_dong=mock.Mock(), toi_da=0.5)

    def test_thieu_file_bat(self):
        with mock.patch.object(cl, "FILE_BAT", os.path.join(tempfile.gettempdir(), "khong_co.bat")):
            with self.assertRaises(FileNotFoundError):
                cl.chay_file_bat(khoi_dong=mock.Mock())


class TestCauHinh(unittest.TestCase):
    def test_luu_va_doc_ip(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(cl, "FILE_CAU_HINH", os.path.join(tmp, "data", "chat_cau_hinh.json")):
                self.assertEqual(cl.doc_cau_hinh(), {})
                cl.luu_cau_hinh(ip_may_chu="192.168.1.5")
                self.assertEqual(cl.doc_cau_hinh()["ip_may_chu"], "192.168.1.5")

    def test_file_hong_thi_tra_ve_rong(self):
        with tempfile.TemporaryDirectory() as tmp:
            duong_dan = os.path.join(tmp, "x.json")
            with open(duong_dan, "w") as f:
                f.write("{khong phai json")
            with mock.patch.object(cl, "FILE_CAU_HINH", duong_dan):
                self.assertEqual(cl.doc_cau_hinh(), {})


@unittest.skipUnless(CO_WEBSOCKETS, "cần thư viện websockets")
class TestKetNoiThat(unittest.TestCase):
    """Chạy server chat thật trên localhost rồi nối/ngắt bằng launcher."""

    def setUp(self):
        from chat_server import MayChuChat, chay_server
        self.cong = cong_trong()
        self.loop = asyncio.new_event_loop()
        san_sang = threading.Event()

        def chay():
            asyncio.set_event_loop(self.loop)
            ev = asyncio.Event()

            async def chinh():
                self.tac_vu = asyncio.ensure_future(
                    chay_server("127.0.0.1", self.cong, MayChuChat(), ev))
                await ev.wait()
                san_sang.set()
                try:
                    await self.tac_vu
                except asyncio.CancelledError:
                    pass
            self.loop.run_until_complete(chinh())

        self.luong = threading.Thread(target=chay, daemon=True)
        self.luong.start()
        self.assertTrue(san_sang.wait(5))

    def tearDown(self):
        self.loop.call_soon_threadsafe(self.tac_vu.cancel)
        self.luong.join(timeout=5)

    def test_ket_noi_va_ngat(self):
        ql = SimpleNamespace(chat=None)
        client = cl.ket_noi(ql, cl.tao_url("127.0.0.1", self.cong))
        try:
            han = time.monotonic() + 5
            while not client.da_ket_noi and time.monotonic() < han:
                time.sleep(0.05)
            self.assertTrue(client.da_ket_noi)
            self.assertIs(ql.chat, client)
        finally:
            cl.ngat_ket_noi(ql)
        self.assertIsNone(ql.chat)

    def test_ket_noi_lai_thay_client_cu(self):
        ql = SimpleNamespace(chat=None)
        url = cl.tao_url("127.0.0.1", self.cong)
        c1 = cl.ket_noi(ql, url)
        c2 = cl.ket_noi(ql, url)
        try:
            self.assertIsNot(c1, c2)
            self.assertIs(ql.chat, c2)
        finally:
            cl.ngat_ket_noi(ql)


if __name__ == "__main__":
    unittest.main()
