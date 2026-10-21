"""Màu sắc, font và style dùng chung cho toàn bộ giao diện."""
from tkinter import ttk

MAU_NEN = "#f1f2f6"
MAU_CHINH = "#2f6fed"
MAU_CHU = "#2d3436"
MAU_CHU_PHU = "#636e72"
MAU_THE = "#ffffff"
MAU_COT = "#e4e7ec"
MAU_COT_SANG = "#d6e4ff" 
MAU_LOI = "#d63031"

# Màu thanh bên trái của thẻ theo mức ưu tiên (khóa phải khớp MUC_UU_TIEN_HOP_LE)
MAU_UU_TIEN = {
    "Thấp": "#2ecc71",
    "Trung bình": "#f1c40f",
    "Cao": "#e67e22",
    "Khẩn": "#e74c3c",
}

# Màu chữ đặt trên nền màu ưu tiên (nền vàng cần chữ tối cho dễ đọc)
MAU_CHU_TREN_UU_TIEN = {
    "Thấp": "white",
    "Trung bình": "#2d3436",
    "Cao": "white",
    "Khẩn": "white",
}

MAU_VIEN_THE = "#d0d4db"
MAU_THE_HOVER = "#f7f9ff"
MAU_HOAN_THANH = "#27ae60"
MAU_CANH_BAO = "#e67e22"

FONT_TIEU_DE = ("Segoe UI", 18, "bold")
FONT_CHUAN = ("Segoe UI", 10)
FONT_DAM = ("Segoe UI", 10, "bold")
FONT_NHO = ("Segoe UI", 9)


def ap_dung_style():
    """Gọi 1 lần sau khi đã tạo tk.Tk() để đồng bộ giao diện các widget ttk."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=MAU_NEN)
    style.configure("TLabel", background=MAU_NEN, foreground=MAU_CHU, font=FONT_CHUAN)
    style.configure("TCheckbutton", background=MAU_NEN, foreground=MAU_CHU, font=FONT_CHUAN)
    style.configure("TButton", font=FONT_CHUAN, padding=6)
    style.configure("Chinh.TButton", font=FONT_DAM, padding=8,
                    background=MAU_CHINH, foreground="white")
    style.map("Chinh.TButton", background=[("active", "#1f56c4")])
    style.configure("TNotebook", background=MAU_NEN)
    style.configure("TNotebook.Tab", font=FONT_DAM, padding=(14, 6))
    style.configure("TEntry", padding=4)