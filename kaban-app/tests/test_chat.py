"""Kiểm thử bình luận thời gian thực: giao thức, đồng bộ vào JSON, server và client WebSocket."""
import asyncio
import json
import os
import socket
import tempfile
import threading
import time
import unittest
from datetime import date, timedelta

from models.BinhLuan import BinhLuan
from services.QuanLyKaban import QuanLyKanban
from services.chat_protocol import dong_goi, giai_ma, tao_phong

try:
    import websockets  # noqa: F401
    CO_WEBSOCKETS = True
except ImportError:
    CO_WEBSOCKETS = False


def _bl(ma="BL-abc123", nguoi="khoa", noi_dung="Xin chào"):
    return BinhLuan(nguoi_gui=nguoi, noi_dung=noi_dung, ma_binh_luan=ma).to_dict()


class TestGiaoThucChat(unittest.TestCase):
    def test_tin_hop_le(self):
        tin = giai_ma(dong_goi({"loai": "binh_luan", "phong": "DA-001/CV-001", "binh_luan": _bl()}))
        self.assertEqual(tin["binh_luan"]["NoiDung"], "Xin chào")
        tin = giai_ma(dong_goi({"loai": "vao_phong", "phong": "DA-001/CV-001", "nguoi": "khoa"}))
        self.assertEqual(tin["nguoi"], "khoa")

    def test_tin_sai_bi_tu_choi(self):
        sai = [
            "khong phai json",
            json.dumps({"phong": "DA-001/CV-001"}),
            json.dumps({"loai": "hack", "phong": "DA-001/CV-001"}),
            json.dumps({"loai": "binh_luan", "phong": "../../etc", "binh_luan": _bl()}),
            json.dumps({"loai": "binh_luan", "phong": "DA-001/CV-001", "binh_luan": {"NoiDung": ""}}),
            json.dumps({"loai": "binh_luan", "phong": "DA-001/CV-001", "binh_luan": _bl(noi_dung="x" * 501)}),
            json.dumps({"loai": "vao_phong", "phong": "DA-001/CV-001", "nguoi": "ten co dau cách"}),
            json.dumps({"loai": "xoa_binh_luan", "phong": "DA-001/CV-001"}),
        ]
        for tho in sai:
            with self.subTest(tho=tho[:40]):
                with self.assertRaises(ValueError):
                    giai_ma(tho)

    def test_tao_phong(self):
        self.assertEqual(tao_phong("DA-001", "CV-002"), "DA-001/CV-002")
        with self.assertRaises(ValueError):
            tao_phong("DA 001", "CV-002")

    def test_ma_binh_luan_khong_trung(self):
        ma = {BinhLuan("khoa", "x").ma_binh_luan for _ in range(500)}
        self.assertEqual(len(ma), 500)


class TestDongBoBinhLuanVaoJson(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.duong_dan = os.path.join(self.tmp.name, "du_an.json")
        self.ql = QuanLyKanban(self.duong_dan, os.path.join(self.tmp.name, "users.json"))
        self.ql.bo_luu_tru.ten_file_nhat_ky = os.path.join(self.tmp.name, "nhat_ky.json")
        self.ql.dang_nhap("admin", "123456")
        self.da = self.ql.tao_du_an("DA-900", "Chat")
        hom_nay = date.today()
        self.cv = self.ql.tao_cong_viec(self.da, {
            "ma_cong_viec": "CV-001", "tieu_de": "Việc", "nguoi_phu_trach": "admin",
            "ngay_bat_dau": hom_nay.isoformat(), "ngay_ket_thuc": (hom_nay + timedelta(days=3)).isoformat(),
            "trang_thai": "Cần làm", "muc_uu_tien": "Thấp", "nhan": "Backend"})

    def test_nhan_binh_luan_luu_json_va_bo_trung(self):
        bl = self.ql.ap_dung_binh_luan_tu_xa(self.da, "CV-001", _bl())
        self.assertIsNotNone(bl)
        self.assertIsNone(self.ql.ap_dung_binh_luan_tu_xa(self.da, "CV-001", _bl()))
        self.assertEqual(len(self.cv.danh_sach_binh_luan), 1)
        moi = QuanLyKanban(self.duong_dan, os.path.join(self.tmp.name, "users.json"))
        cv = moi.tim_du_an_theo_ma("DA-900").tim_cong_viec_theo_ma("CV-001")
        self.assertEqual(cv.danh_sach_binh_luan[0].ma_binh_luan, "BL-abc123")

    def test_nhan_xoa_binh_luan(self):
        self.ql.ap_dung_binh_luan_tu_xa(self.da, "CV-001", _bl())
        self.assertTrue(self.ql.ap_dung_xoa_binh_luan_tu_xa(self.da, "CV-001", "BL-abc123"))
        self.assertFalse(self.ql.ap_dung_xoa_binh_luan_tu_xa(self.da, "CV-001", "BL-abc123"))
        self.assertEqual(self.cv.danh_sach_binh_luan, [])

    def test_cong_viec_khong_ton_tai_thi_bo_qua(self):
        self.assertIsNone(self.ql.ap_dung_binh_luan_tu_xa(self.da, "CV-999", _bl()))
        self.assertFalse(self.ql.ap_dung_xoa_binh_luan_tu_xa(self.da, "CV-999", "BL-abc123"))


def _cong_trong():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@unittest.skipUnless(CO_WEBSOCKETS, "Chưa cài thư viện websockets")
class TestServerVaClientWebSocket(unittest.TestCase):
    PHONG = "DA-001/CV-001"

    def setUp(self):
        from chat_server import MayChuChat, chay_server
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log = os.path.join(self.tmp.name, "chat_log.jsonl")
        self.cong = _cong_trong()
        self.may_chu = MayChuChat(duong_dan_log=self.log)
        self.loop = asyncio.new_event_loop()
        san_sang = threading.Event()

        def chay():
            asyncio.set_event_loop(self.loop)
            su_kien = asyncio.Event()
            self.task = self.loop.create_task(chay_server("127.0.0.1", self.cong, self.may_chu, su_kien))
            self.loop.create_task(self._bao(su_kien, san_sang))
            try:
                self.loop.run_until_complete(self.task)
            except asyncio.CancelledError:
                pass

        self.luong = threading.Thread(target=chay, daemon=True)
        self.luong.start()
        self.assertTrue(san_sang.wait(5), "Server không khởi động được")
        self.addCleanup(self._dung_server)
        self.url = f"ws://127.0.0.1:{self.cong}"

    async def _bao(self, su_kien, san_sang):
        await su_kien.wait()
        san_sang.set()

    def _dung_server(self):
        self.loop.call_soon_threadsafe(self.task.cancel)
        self.luong.join(5)

    def _client(self):
        from services.chat_client import ChatClient
        c = ChatClient(self.url)
        c.bat_dau()
        self.addCleanup(c.dung)
        return c

    @staticmethod
    def _cho(dieu_kien, giay=5):
        het = time.time() + giay
        while time.time() < het:
            if dieu_kien():
                return True
            time.sleep(0.05)
        return False

    @staticmethod
    def _lay(q, loai, giay=5):
        het = time.time() + giay
        while time.time() < het:
            try:
                tin = q.get(timeout=0.1)
            except Exception:
                continue
            if tin["loai"] == loai:
                return tin
        return None

    def test_hai_client_nhan_binh_luan_cua_nhau(self):
        a, b = self._client(), self._client()
        qa = a.vao_phong(self.PHONG, "khoa")
        qb = b.vao_phong(self.PHONG, "huy")
        self.assertIsNotNone(self._lay(qa, "lich_su"))
        self.assertIsNotNone(self._lay(qb, "lich_su"))

        a.gui({"loai": "binh_luan", "phong": self.PHONG, "binh_luan": _bl(nguoi="khoa")})
        tin = self._lay(qb, "binh_luan")
        self.assertIsNotNone(tin, "Client B không nhận được bình luận")
        self.assertEqual(tin["binh_luan"]["NguoiGui"], "khoa")
        self.assertIsNone(self._lay(qa, "binh_luan", giay=0.5), "Người gửi không được nhận lại tin của mình")

        b.gui({"loai": "xoa_binh_luan", "phong": self.PHONG, "ma_binh_luan": "BL-abc123", "nguoi": "huy"})
        self.assertIsNotNone(self._lay(qa, "xoa_binh_luan"))

    def test_phong_khac_khong_nhan_tin(self):
        a, b = self._client(), self._client()
        qa = a.vao_phong(self.PHONG, "khoa")
        qb = b.vao_phong("DA-001/CV-002", "huy")
        self._lay(qa, "lich_su")
        self._lay(qb, "lich_su")
        a.gui({"loai": "binh_luan", "phong": self.PHONG, "binh_luan": _bl()})
        self.assertIsNone(self._lay(qb, "binh_luan", giay=0.7))

    def test_vao_sau_nhan_lich_su_va_log_chi_noi_them(self):
        a = self._client()
        qa = a.vao_phong(self.PHONG, "khoa")
        self._lay(qa, "lich_su")
        a.gui({"loai": "binh_luan", "phong": self.PHONG, "binh_luan": _bl("BL-000001")})
        a.gui({"loai": "binh_luan", "phong": self.PHONG, "binh_luan": _bl("BL-000002")})
        self.assertTrue(self._cho(lambda: len(self.may_chu.lich_su[self.PHONG]) == 2))

        b = self._client()
        qb = b.vao_phong(self.PHONG, "huy")
        tin = self._lay(qb, "lich_su")
        self.assertEqual([bl["MaBinhLuan"] for bl in tin["danh_sach"]], ["BL-000001", "BL-000002"])

        with open(self.log, encoding="utf-8") as f:
            truoc = f.read()
        a.gui({"loai": "xoa_binh_luan", "phong": self.PHONG, "ma_binh_luan": "BL-000001"})
        self.assertTrue(self._cho(lambda: len(self.may_chu.lich_su[self.PHONG]) == 1))
        with open(self.log, encoding="utf-8") as f:
            sau = f.read()
        self.assertTrue(sau.startswith(truoc), "Nhật ký chat phải chỉ nối thêm")
        self.assertEqual(len(sau.splitlines()), 3)

    def test_client_ket_noi_lai_va_gui_tin_cho(self):
        a = self._client()
        qa = a.vao_phong(self.PHONG, "khoa")
        self._lay(qa, "lich_su")
        self.assertTrue(self._cho(lambda: a.da_ket_noi))
        cu = set(self.may_chu.phong[self.PHONG])
        for ws in cu:                                             # server ngắt kết nối của A
            asyncio.run_coroutine_threadsafe(ws.close(), self.loop).result(5)
        self.assertTrue(self._cho(lambda: bool(self.may_chu.phong[self.PHONG] - cu), giay=8),
                        "Client không tự kết nối lại và vào lại phòng")

        b = self._client()
        qb = b.vao_phong(self.PHONG, "huy")
        self._lay(qb, "lich_su")
        self.assertTrue(self._cho(lambda: len(self.may_chu.phong[self.PHONG]) == 2, giay=8))
        a.gui({"loai": "binh_luan", "phong": self.PHONG, "binh_luan": _bl()})
        self.assertIsNotNone(self._lay(qb, "binh_luan"), "Sau khi kết nối lại A vẫn phải gửi được")

    def test_server_tra_loi_khi_tin_sai_va_khong_sap(self):
        from websockets.sync.client import connect
        with connect(self.url) as ws:
            ws.send("rác")
            self.assertEqual(json.loads(ws.recv(timeout=5))["loai"], "loi")
            ws.send(dong_goi({"loai": "binh_luan", "phong": self.PHONG, "binh_luan": _bl()}))
            self.assertIn("Chưa vào phòng", json.loads(ws.recv(timeout=5))["thong_diep"])
        a = self._client()
        self.assertIsNotNone(self._lay(a.vao_phong(self.PHONG, "khoa"), "lich_su"))

    def test_server_nap_lai_lich_su_tu_log(self):
        from chat_server import MayChuChat
        a = self._client()
        qa = a.vao_phong(self.PHONG, "khoa")
        self._lay(qa, "lich_su")
        a.gui({"loai": "binh_luan", "phong": self.PHONG, "binh_luan": _bl()})
        self.assertTrue(self._cho(lambda: os.path.exists(self.log) and os.path.getsize(self.log) > 0))
        moi = MayChuChat(duong_dan_log=self.log)
        self.assertEqual(moi.lich_su[self.PHONG][0]["MaBinhLuan"], "BL-abc123")


if __name__ == "__main__":
    unittest.main()
