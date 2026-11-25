"""services.chat_client: Client WebSocket chạy nền cho bình luận thời gian thực.

Client chạy vòng lặp asyncio trên một luồng riêng để không chặn Tkinter. Giao diện chỉ gọi các hàm
thread-safe (vao_phong, roi_phong, gui) và đọc tin đến từ queue.Queue của từng phòng bằng `after()`.
Mất kết nối thì tự kết nối lại; tin gửi lúc mất mạng được giữ lại (tối đa 200) và gửi khi có mạng.
"""
import asyncio
import queue
import threading

from logger import logger
from services.chat_protocol import KICH_THUOC_TIN_TOI_DA, dong_goi, giai_ma

SO_TIN_CHO_TOI_DA = 200
THOI_GIAN_CHO_KET_NOI_LAI = (1, 2, 5, 10)   # giây, tăng dần


class ChatClient:
    def __init__(self, url: str):
        if not url.startswith(("ws://", "wss://")):
            raise ValueError("Địa chỉ server chat phải bắt đầu bằng ws:// hoặc wss://")
        self.url = url
        self.da_ket_noi = False
        self._phong = {}             # phong -> {"nguoi": str, "hang_doi": [queue.Queue]}
        self._khoa = threading.Lock()
        self._loop = None
        self._hang_doi_gui = None    # asyncio.Queue, tạo trong luồng nền
        self._dung = threading.Event()
        self._luong = None
        self._san_sang = threading.Event()

    # ==================== API cho giao diện (thread-safe) ====================
    def bat_dau(self):
        if self._luong and self._luong.is_alive():
            return
        self._dung.clear()
        self._luong = threading.Thread(target=self._chay_luong, name="ChatClient", daemon=True)
        self._luong.start()
        self._san_sang.wait(timeout=5)

    def dung(self):
        self._dung.set()
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(lambda: None)   # đánh thức vòng lặp
        if self._luong:
            self._luong.join(timeout=5)

    def vao_phong(self, phong: str, nguoi: str) -> queue.Queue:
        """Đăng ký nhận tin của một phòng; trả về hàng đợi tin đến cho giao diện đọc."""
        hang_doi = queue.Queue()
        with self._khoa:
            muc = self._phong.setdefault(phong, {"nguoi": nguoi, "hang_doi": []})
            muc["nguoi"] = nguoi
            muc["hang_doi"].append(hang_doi)
            lan_dau = len(muc["hang_doi"]) == 1
        if lan_dau:
            self.gui({"loai": "vao_phong", "phong": phong, "nguoi": nguoi})
        return hang_doi

    def roi_phong(self, phong: str, hang_doi: queue.Queue):
        with self._khoa:
            muc = self._phong.get(phong)
            if not muc:
                return
            if hang_doi in muc["hang_doi"]:
                muc["hang_doi"].remove(hang_doi)
            con_nguoi = bool(muc["hang_doi"])
            if not con_nguoi:
                del self._phong[phong]
        if not con_nguoi:
            self.gui({"loai": "roi_phong", "phong": phong})

    def gui(self, tin: dict):
        """Xếp tin vào hàng gửi; không bao giờ chặn giao diện."""
        if self._loop is None or self._hang_doi_gui is None or self._loop.is_closed():
            return
        self._loop.call_soon_threadsafe(self._xep_hang, tin)

    # ==================== Luồng nền ====================
    def _xep_hang(self, tin):
        if self._hang_doi_gui.qsize() >= SO_TIN_CHO_TOI_DA:
            self._hang_doi_gui.get_nowait()   # bỏ tin cũ nhất khi mất mạng quá lâu
        self._hang_doi_gui.put_nowait(tin)

    def _chay_luong(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._hang_doi_gui = asyncio.Queue()
        self._san_sang.set()
        try:
            self._loop.run_until_complete(self._vong_ket_noi())
        finally:
            self._loop.close()

    async def _vong_ket_noi(self):
        from websockets.asyncio.client import connect
        from websockets.exceptions import WebSocketException

        lan_thu = 0
        while not self._dung.is_set():
            try:
                async with connect(self.url, open_timeout=5, max_size=KICH_THUOC_TIN_TOI_DA) as ws:
                    self.da_ket_noi, lan_thu = True, 0
                    logger.info(f"Đã kết nối server bình luận {self.url}")
                    with self._khoa:
                        dang_ky = [(p, m["nguoi"]) for p, m in self._phong.items()]
                    for phong, nguoi in dang_ky:   # vào lại các phòng sau khi kết nối lại
                        await ws.send(dong_goi({"loai": "vao_phong", "phong": phong, "nguoi": nguoi}))
                    await self._phien(ws)
            except (OSError, asyncio.TimeoutError, WebSocketException) as loi:
                if self.da_ket_noi:
                    logger.warning(f"Mất kết nối server bình luận: {loi}")
                elif lan_thu == 0:
                    logger.warning(f"Không kết nối được server bình luận {self.url}: {loi}")
            self.da_ket_noi = False
            if self._dung.is_set():
                break
            cho = THOI_GIAN_CHO_KET_NOI_LAI[min(lan_thu, len(THOI_GIAN_CHO_KET_NOI_LAI) - 1)]
            lan_thu += 1
            await self._ngu(cho)

    async def _ngu(self, giay):
        buoc = 0.1
        while giay > 0 and not self._dung.is_set():
            await asyncio.sleep(buoc)
            giay -= buoc

    async def _phien(self, ws):
        nhan = asyncio.ensure_future(self._nhan(ws))
        gui = asyncio.ensure_future(self._gui(ws))
        canh = asyncio.ensure_future(self._canh_dung())
        xong, cho = await asyncio.wait({nhan, gui, canh}, return_when=asyncio.FIRST_COMPLETED)
        for t in cho:
            t.cancel()
        for t in xong:
            if t is not canh and t.exception():
                raise t.exception()

    async def _canh_dung(self):
        while not self._dung.is_set():
            await asyncio.sleep(0.1)

    async def _gui(self, ws):
        while True:
            tin = await self._hang_doi_gui.get()
            try:
                await ws.send(dong_goi(tin))
            except BaseException:   # gồm cả CancelledError khi phiên kết thúc
                # Chưa gửi được: đưa lại đầu hàng để gửi sau khi kết nối lại
                cu = [tin]
                while not self._hang_doi_gui.empty():
                    cu.append(self._hang_doi_gui.get_nowait())
                for t in cu:
                    self._hang_doi_gui.put_nowait(t)
                raise

    async def _nhan(self, ws):
        async for tho in ws:
            try:
                tin = giai_ma(tho)
            except ValueError as loi:
                logger.warning(f"Bỏ qua tin sai giao thức từ server: {loi}")
                continue
            if tin["loai"] == "loi":
                logger.warning(f"Server bình luận báo lỗi: {tin['thong_diep']}")
                continue
            with self._khoa:
                hang_doi = list(self._phong.get(tin["phong"], {}).get("hang_doi", []))
            for q in hang_doi:
                q.put(tin)
