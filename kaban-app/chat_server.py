"""chat_server.py: Server WebSocket chuyển tiếp bình luận thời gian thực giữa các máy trong mạng LAN.

Cách chạy (trên một máy trong LAN):
    python chat_server.py                      # lắng nghe 0.0.0.0:8765
    python chat_server.py --port 9000

Các máy khác mở ứng dụng với:
    python main.py --chat ws://<IP máy chạy server>:8765

Server chỉ chuyển tiếp tin trong cùng một phòng (một công việc) và giữ tối đa 50 bình luận gần nhất
mỗi phòng để gửi cho máy vào sau. Mọi sự kiện được nối thêm vào data/chat_log.jsonl (không ghi đè).
Lưu ý: server tin tên người gửi do client khai báo, chỉ phù hợp để demo trong mạng LAN tin cậy.
"""
import argparse
import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime

from websockets.asyncio.server import broadcast, serve
from websockets.exceptions import ConnectionClosed

from config import THU_MUC_DATA
from logger import logger
from services.chat_protocol import KICH_THUOC_TIN_TOI_DA, dong_goi, giai_ma

LICH_SU_TOI_DA = 50
TEN_FILE_LOG_CHAT = os.path.join(THU_MUC_DATA, "chat_log.jsonl")


class MayChuChat:
    """Quản lý phòng, lịch sử và nhật ký; không phụ thuộc giao diện."""

    def __init__(self, duong_dan_log=TEN_FILE_LOG_CHAT, lich_su_toi_da=LICH_SU_TOI_DA):
        self.duong_dan_log = duong_dan_log
        self.lich_su_toi_da = lich_su_toi_da
        self.phong = defaultdict(set)      # phong -> {websocket}
        self.lich_su = defaultdict(list)   # phong -> [BinhLuan dict]
        self._nap_lich_su()

    # ---------- Lịch sử & nhật ký ----------
    def _nap_lich_su(self):
        if not self.duong_dan_log or not os.path.exists(self.duong_dan_log):
            return
        with open(self.duong_dan_log, encoding="utf-8") as f:
            for dong in f:
                try:
                    self._cap_nhat_lich_su(giai_ma(json.loads(dong)["tin"]))
                except (ValueError, KeyError, TypeError):
                    continue   # bỏ qua dòng hỏng, không làm sập server

    def _cap_nhat_lich_su(self, tin):
        ds = self.lich_su[tin["phong"]]
        if tin["loai"] == "binh_luan":
            ma = tin["binh_luan"]["MaBinhLuan"]
            if all(bl["MaBinhLuan"] != ma for bl in ds):
                ds.append(tin["binh_luan"])
                del ds[:-self.lich_su_toi_da]
        elif tin["loai"] == "xoa_binh_luan":
            ds[:] = [bl for bl in ds if bl["MaBinhLuan"] != tin["ma_binh_luan"]]

    def _ghi_log(self, tin):
        if not self.duong_dan_log:
            return
        try:
            os.makedirs(os.path.dirname(self.duong_dan_log) or ".", exist_ok=True)
            with open(self.duong_dan_log, "a", encoding="utf-8") as f:
                f.write(json.dumps({"thoi_gian": datetime.now().isoformat(), "tin": dong_goi(tin)},
                                   ensure_ascii=False) + "\n")
        except OSError as loi:
            logger.error(f"Không ghi được nhật ký chat: {loi}")

    # ---------- Xử lý kết nối ----------
    async def xu_ly(self, ws):
        da_vao = set()
        try:
            async for tho in ws:
                try:
                    tin = giai_ma(tho)
                except ValueError as loi:
                    await ws.send(dong_goi({"loai": "loi", "thong_diep": str(loi)}))
                    continue
                loai, phong = tin["loai"], tin.get("phong")
                if loai == "vao_phong":
                    self.phong[phong].add(ws)
                    da_vao.add(phong)
                    await ws.send(dong_goi({"loai": "lich_su", "phong": phong,
                                            "danh_sach": list(self.lich_su[phong])}))
                elif loai == "roi_phong":
                    self.phong[phong].discard(ws)
                    da_vao.discard(phong)
                elif loai in ("binh_luan", "xoa_binh_luan"):
                    if phong not in da_vao:
                        await ws.send(dong_goi({"loai": "loi", "thong_diep": "Chưa vào phòng " + phong}))
                        continue
                    self._cap_nhat_lich_su(tin)
                    self._ghi_log(tin)
                    broadcast([k for k in self.phong[phong] if k is not ws], dong_goi(tin))
                else:
                    await ws.send(dong_goi({"loai": "loi", "thong_diep": f"Client không được gửi '{loai}'"}))
        except ConnectionClosed:
            pass
        finally:
            for phong in da_vao:
                self.phong[phong].discard(ws)


async def chay_server(host="0.0.0.0", port=8765, may_chu=None, san_sang=None):
    """Chạy server tới khi bị hủy. `san_sang` (asyncio.Event) được set khi đã lắng nghe."""
    may_chu = may_chu or MayChuChat()
    async with serve(may_chu.xu_ly, host, port, max_size=KICH_THUOC_TIN_TOI_DA) as server:
        logger.info(f"Server bình luận đang lắng nghe ws://{host}:{port}")
        if san_sang is not None:
            san_sang.set()
        await server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Server WebSocket bình luận thời gian thực cho Kanban App")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        asyncio.run(chay_server(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Đã dừng server bình luận")


if __name__ == "__main__":
    main()
