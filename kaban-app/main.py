"""main.py: Điểm khởi chạy duy nhất (Entry point) hợp nhất toàn bộ Backend và Frontend.

Cách chạy:
    - Chạy bình thường (giao diện đăng nhập):  python main.py
    - Chạy thẳng với quyền Admin:              python main.py --admin
    - Chạy chế độ Terminal/CLI:               python main.py --cli
    - Bật bình luận realtime (WebSocket):      python main.py --chat ws://192.168.1.10:8765
      (hoặc đặt biến môi trường KANBAN_CHAT_URL; server chạy bằng `python chat_server.py`)
"""
import os
import shutil
import sys
import tkinter as tk

from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
from services.QuanLyKaban import QuanLyKanban
from ui.styles import theme
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from logger import logger


def chay_che_do_cli(ql: QuanLyKanban):
    """Chạy chế độ console terminal để in nhanh danh sách dự án."""
    print("=" * 60)
    print("             ỨNG DỤNG QUẢN LÝ TIẾN ĐỘ KANBAN (CLI)")
    print("=" * 60)
    try:
        ql.dang_nhap("admin", "123456")
        ds = ql.lay_danh_sach_du_an()
        if not ds:
            print("Chưa có dự án nào trong hệ thống.")
            return
        for da in ds:
            print(f"\n[DỰ ÁN] {da.ma_du_an} — {da.ten_du_an} ({len(da.cong_viec)} công việc)")
            for cv in da.cong_viec:
                print(f"  • [{cv.ma_cong_viec}] {cv.tieu_de:<30} | {cv.trang_thai:<12} | Ưu tiên: {cv.muc_uu_tien}")
    except Exception as err:
        print(f"Lỗi CLI: {err}")
    print("=" * 60)


def chay_giao_dien(ql: QuanLyKanban):
    """Khởi chạy ứng dụng giao diện đồ họa (GUI) chuẩn Figma."""
    goc = tk.Tk()
    goc.withdraw()
    theme.ap_dung_style()

    def mo_dang_nhap():
        LoginWindow(goc, ql, mo_cua_so_chinh)

    def mo_cua_so_chinh(_nguoi_dung):
        MainWindow(goc, ql, khi_dang_xuat=mo_dang_nhap)

    # Nếu truyền cờ --admin hoặc --direct thì tự động đăng nhập admin
    if "--admin" in sys.argv or "--direct" in sys.argv:
        try:
            nd = ql.dang_nhap("admin", "123456")
            mo_cua_so_chinh(nd)
        except Exception as err:
            logger.warning(f"Không thể tự đăng nhập admin: {err}. Mở màn hình đăng nhập.")
            mo_dang_nhap()
    else:
        mo_dang_nhap()

    goc.mainloop()


def chuan_bi_du_lieu_khi_dong_goi():
    """Khi chạy từ file .exe (PyInstaller): chép dữ liệu mẫu đã đóng gói ra thư mục data cạnh file .exe.

    Dữ liệu cần nằm cạnh .exe để ghi được và còn nguyên sau khi tắt ứng dụng. Nếu thư mục data
    đã có du_an.json thì giữ nguyên, không ghi đè dữ liệu của người dùng. Chạy bằng `python main.py` thì bỏ qua.
    """
    if not getattr(sys, "frozen", False):
        return
    nguon = os.path.join(getattr(sys, "_MEIPASS", ""), "data")
    dich = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "data")
    if os.path.isdir(nguon) and not os.path.exists(os.path.join(dich, "du_an.json")):
        try:
            shutil.copytree(nguon, dich, dirs_exist_ok=True, ignore=shutil.ignore_patterns("backup"))
            logger.info(f"Đã chép dữ liệu mẫu ra '{dich}'")
        except OSError as loi:
            logger.error(f"Không chép được dữ liệu mẫu (thư mục có thể không cho ghi): {loi}")


def lay_dia_chi_chat(argv=None):
    """Lấy địa chỉ server bình luận từ `--chat <url>` hoặc biến môi trường KANBAN_CHAT_URL."""
    argv = sys.argv if argv is None else argv
    if "--chat" in argv:
        i = argv.index("--chat")
        if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            return argv[i + 1]
        logger.warning("Thiếu địa chỉ sau --chat, ví dụ: --chat ws://192.168.1.10:8765")
        return None
    return os.environ.get("KANBAN_CHAT_URL") or None


def ket_noi_chat(ql: QuanLyKanban, url):
    """Gắn ChatClient vào ql nếu có địa chỉ server; lỗi thì chạy ngoại tuyến như cũ."""
    if not url:
        return None
    try:
        from services.chat_client import ChatClient
        client = ChatClient(url)
    except ImportError:
        logger.warning("Chưa cài thư viện 'websockets' (pip install -r requirements.txt); bình luận chạy ngoại tuyến.")
        return None
    except ValueError as loi:
        logger.warning(f"{loi}; bình luận chạy ngoại tuyến.")
        return None
    client.bat_dau()
    ql.chat = client
    return client


def main():
    chuan_bi_du_lieu_khi_dong_goi()
    logger.info("Khởi động Ứng dụng Quản lý Kanban...")
    ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)

    if "--cli" in sys.argv:
        chay_che_do_cli(ql)
    else:
        ket_noi_chat(ql, lay_dia_chi_chat())
        try:
            chay_giao_dien(ql)
        finally:
            client = getattr(ql, "chat", None)   # gồm cả client bật từ nút Chat trong ứng dụng
            if client is not None:
                client.dung()

if __name__ == "__main__":
    main()
