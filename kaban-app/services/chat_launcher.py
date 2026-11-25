"""services.chat_launcher: Bật server chat bằng file .bat và nối ứng dụng vào server (cho nút "Chat").

Không phụ thuộc giao diện nên kiểm thử được độc lập. Giao diện chỉ gọi các hàm bên dưới.
"""
import json
import os
import re
import socket
import sys
import time

from config import THU_MUC_DATA, THU_MUC_GOC
from logger import logger

CONG_MAC_DINH = 8765
FILE_BAT = os.path.join(THU_MUC_GOC, "chat_server.bat")
FILE_CAU_HINH = os.path.join(THU_MUC_DATA, "chat_cau_hinh.json")

_MAU_HOST = re.compile(r"[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?")


def lay_ip_lan() -> str:
    """IP của máy trong mạng LAN/Wi-Fi (không gửi gói tin nào ra ngoài); lỗi thì trả về 127.0.0.1."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def tao_url(host: str, cong: int = CONG_MAC_DINH) -> str:
    return f"ws://{host}:{cong}"


def chuan_hoa_dia_chi(chuoi: str, cong_mac_dinh: int = CONG_MAC_DINH) -> str:
    """Nhận '192.168.1.10', '192.168.1.10:9000' hoặc 'ws://192.168.1.10:9000' -> 'ws://host:cong'.

    Ném ValueError (thông điệp tiếng Việt) nếu không hợp lệ.
    """
    s = (chuoi or "").strip()
    s = re.sub(r"^(ws|wss|http|https)://", "", s, flags=re.IGNORECASE).rstrip("/")
    if not s:
        raise ValueError("Hãy nhập IP của máy chủ chat, ví dụ 192.168.1.10")
    host, cong = s, cong_mac_dinh
    if ":" in s:
        host, _, cong_chuoi = s.rpartition(":")
        if not cong_chuoi.isdigit() or not (1 <= int(cong_chuoi) <= 65535):
            raise ValueError("Cổng phải là số từ 1 đến 65535, ví dụ 192.168.1.10:8765")
        cong = int(cong_chuoi)
    if not _MAU_HOST.fullmatch(host):
        raise ValueError("Địa chỉ không hợp lệ. Hãy nhập IP dạng 192.168.1.10")
    return tao_url(host, cong)


def tach_url(url: str):
    """'ws://host:cong' -> (host, cong)."""
    phan = re.sub(r"^wss?://", "", url).rstrip("/")
    host, _, cong = phan.rpartition(":")
    return host, int(cong)


def cong_dang_mo(host: str, cong: int = CONG_MAC_DINH, cho: float = 0.6) -> bool:
    """True nếu có chương trình đang lắng nghe tại host:cong."""
    try:
        with socket.create_connection((host, cong), timeout=cho):
            return True
    except OSError:
        return False


def cho_server_san_sang(host: str, cong: int = CONG_MAC_DINH, toi_da: float = 10.0) -> bool:
    han = time.monotonic() + toi_da
    while time.monotonic() < han:
        if cong_dang_mo(host, cong):
            return True
        time.sleep(0.3)
    return False


def chay_file_bat(khoi_dong=None):
    """Mở chat_server.bat trong cửa sổ console riêng (đóng cửa sổ đó là tắt server)."""
    if not os.path.isfile(FILE_BAT):
        raise FileNotFoundError(f"Không tìm thấy {FILE_BAT}")
    if khoi_dong is None:
        if sys.platform != "win32":
            raise OSError("Nút này chạy file .bat nên chỉ dùng được trên Windows")
        khoi_dong = os.startfile
    khoi_dong(FILE_BAT)


def bat_may_chu(khoi_dong=None, toi_da: float = 10.0) -> str:
    """Bảo đảm server chat đang chạy trên máy này. Trả về địa chỉ để máy NÀY kết nối (ws://127.0.0.1:...).

    Nếu cổng đã mở sẵn (server chạy từ trước) thì không chạy thêm.
    """
    if not cong_dang_mo("127.0.0.1"):
        chay_file_bat(khoi_dong)
        if not cho_server_san_sang("127.0.0.1", toi_da=toi_da):
            raise TimeoutError(
                "Server chưa lên sau vài giây. Xem cửa sổ đen vừa mở để biết lỗi "
                "(thường là thiếu Python hoặc thư viện websockets)."
            )
    return tao_url("127.0.0.1")


# ==================== Nối / ngắt ứng dụng với server ====================
def ket_noi(ql, url: str):
    """Tạo ChatClient mới, gắn vào ql.chat (thay client cũ nếu có)."""
    from services.chat_client import ChatClient   # ImportError nếu chưa cài websockets
    ngat_ket_noi(ql)
    client = ChatClient(url)
    client.bat_dau()
    ql.chat = client
    return client


def ngat_ket_noi(ql):
    cu = getattr(ql, "chat", None)
    if cu is not None:
        try:
            cu.dung()
        except Exception as loi:   # không để lỗi đóng kết nối làm sập giao diện
            logger.warning(f"Lỗi khi ngắt kết nối chat: {loi}")
    ql.chat = None


# ==================== Nhớ IP đã dùng ====================
def doc_cau_hinh() -> dict:
    try:
        with open(FILE_CAU_HINH, encoding="utf-8") as f:
            du_lieu = json.load(f)
        return du_lieu if isinstance(du_lieu, dict) else {}
    except (OSError, ValueError):
        return {}


def luu_cau_hinh(**gia_tri):
    du_lieu = doc_cau_hinh()
    du_lieu.update(gia_tri)
    try:
        os.makedirs(os.path.dirname(FILE_CAU_HINH), exist_ok=True)
        with open(FILE_CAU_HINH, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=2)
    except OSError as loi:
        logger.warning(f"Không lưu được cấu hình chat: {loi}")
