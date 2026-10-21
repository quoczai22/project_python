"""Các hàm tiện ích nhỏ dùng chung cho các cửa sổ."""


def can_giua(cua_so, rong=None, cao=None):
    """Đặt cửa sổ vào giữa màn hình. Bỏ trống rong/cao thì tự lấy đúng cỡ nội dung cần."""
    cua_so.update_idletasks()
    rong = rong or cua_so.winfo_reqwidth()
    cao = cao or cua_so.winfo_reqheight()
    x = (cua_so.winfo_screenwidth() - rong) // 2
    y = (cua_so.winfo_screenheight() - cao) // 2
    cua_so.geometry(f"{rong}x{cao}+{x}+{y}")