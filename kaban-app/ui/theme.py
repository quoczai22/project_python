"""Màu sắc, font, style chuẩn Figma (Design Kanban Modals) kết hợp Tkinter & CustomTkinter."""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# Bảng màu chuẩn từ thiết kế Figma (Design Kanban Modals)
MAU_NEN = "#edf2f5"            # --canvas
MAU_CHINH = "#176b63"          # --primary (Teal đậm hiện đại)
MAU_CHINH_DAM = "#11564f"      # --primary-dark (Hover)
MAU_CHINH_NHAT = "#e4f3f0"     # --primary-soft
MAU_NHAN = "#e9a23b"           # --accent (Vàng hổ phách)

MAU_CHU = "#15263c"            # --ink
MAU_CHU_NHAN = "#3e5066"       # màu label form
MAU_CHU_PHU = "#718096"        # --muted
MAU_THE = "#ffffff"            # --surface
MAU_O_NHAP = "#fbfcfd"         # nền control input
MAU_COT = "#e2e9ef"            # nền cột Kanban
MAU_COT_SANG = "#d4eae6"       # nền cột khi kéo thả thẻ vào
MAU_VIEN = "#dce4eb"           # --line
MAU_VIEN_THE = "#cad5df"       # --line-strong
MAU_THE_HOVER = "#f4f9f8"      # nền thẻ khi rê chuột

MAU_LOI = "#e53e3e"
MAU_HOAN_THANH = "#176b63"
MAU_CANH_BAO = "#dd6b20"

# Màu thanh bên trái & badge của thẻ theo mức ưu tiên (khớp MUC_UU_TIEN_HOP_LE)
MAU_UU_TIEN = {
    "Thấp": "#2f9e66",
    "Trung bình": "#e9a23b",
    "Cao": "#dd6b20",
    "Khẩn": "#e53e3e",
}

MAU_NEN_BADGE_UU_TIEN = {
    "Thấp": "#e6f6ee",
    "Trung bình": "#fef5e7",
    "Cao": "#feebc8",
    "Khẩn": "#fed7d7",
}

MAU_CHU_TREN_UU_TIEN = {
    "Thấp": "white",
    "Trung bình": "#15263c",
    "Cao": "white",
    "Khẩn": "white",
}

FONT_TIEU_DE = ("Segoe UI", 17, "bold")
FONT_PHU_DE = ("Segoe UI", 13, "bold")
FONT_CHUAN = ("Segoe UI", 10)
FONT_DAM = ("Segoe UI", 10, "bold")
FONT_NHO = ("Segoe UI", 9)
FONT_EYEBROW = ("Segoe UI", 8, "bold")


def ap_dung_style():
    """Thiết lập chế độ sáng cho CustomTkinter và đồng bộ ttk.Style."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=MAU_NEN)
    style.configure("Card.TFrame", background=MAU_THE)
    style.configure("TLabel", background=MAU_NEN, foreground=MAU_CHU, font=FONT_CHUAN)
    style.configure("TCheckbutton", background=MAU_THE, foreground=MAU_CHU, font=FONT_CHUAN)
    style.configure("TButton", font=FONT_CHUAN, padding=6,
                    background=MAU_THE, foreground=MAU_CHU)
    style.configure("Chinh.TButton", font=FONT_DAM, padding=8,
                    background=MAU_CHINH, foreground="white")
    style.map("Chinh.TButton", background=[("active", MAU_CHINH_DAM)])
    style.configure("TNotebook", background=MAU_NEN, borderwidth=0)
    style.configure("TNotebook.Tab", font=FONT_DAM, padding=(16, 8),
                    background=MAU_VIEN, foreground=MAU_CHU_NHAN)
    style.map("TNotebook.Tab",
              background=[("selected", MAU_THE)],
              foreground=[("selected", MAU_CHINH)])
    style.configure("TEntry", padding=6)

    # Style cho Treeview hiện đại
    style.configure("Treeview",
                    background=MAU_THE,
                    fieldbackground=MAU_THE,
                    foreground=MAU_CHU,
                    rowheight=30,
                    borderwidth=1,
                    font=FONT_CHUAN)
    style.configure("Treeview.Heading",
                    background=MAU_NEN,
                    foreground=MAU_CHU_NHAN,
                    font=FONT_DAM,
                    padding=(8, 6))
    style.map("Treeview",
              background=[("selected", MAU_CHINH_NHAT)],
              foreground=[("selected", MAU_CHINH)])


def tao_header_figma(cha, eyebrow: str, tieu_de: str, badge_text: str = None, cao: int = 84):
    """
    Tạo thanh Header màu Teal đậm (#176b63) chuẩn thiết kế Figma (Design Kanban Modals):
    - Bên trái: Biểu tượng 3 cột Kanban (brand-mark) + dòng chữ nhỏ eyebrow + tiêu đề lớn.
    - Bên phải: Vòng tròn trang trí mờ và/hoặc huy hiệu (badge_text như 'CV', 'DA', 'TK').
    """
    header = tk.Canvas(cha, bg=MAU_CHINH, height=cao, highlightthickness=0, bd=0)
    header.pack(fill="x", side="top")

    # Vẽ vòng tròn trang trí mờ góc phải dưới giống .modal-header::after trong Figma
    def _ve_trang_tri(event=None):
        header.delete("decor")
        w = header.winfo_width()
        if w > 50:
            header.create_oval(w - 130, cao - 95, w + 45, cao + 80,
                               outline="#237a72", width=24, tags="decor")

    header.bind("<Configure>", _ve_trang_tri)

    noi_dung = tk.Frame(header, bg=MAU_CHINH)
    noi_dung.pack(fill="both", expand=True, padx=26, pady=14)

    # Biểu tượng 3 thanh Kanban (brand-mark trong Figma)
    khung_logo = ctk.CTkFrame(noi_dung, width=42, height=42, corner_radius=10,
                              fg_color="#287870", border_width=1, border_color="#3c8981")
    khung_logo.pack(side="left", padx=(0, 14))
    khung_logo.pack_propagate(False)

    cv_logo = tk.Canvas(khung_logo, width=26, height=24, bg="#287870",
                        highlightthickness=0, bd=0)
    cv_logo.place(relx=0.5, rely=0.5, anchor="center")
    # 3 cột dọc tượng trưng bảng Kanban
    cv_logo.create_rectangle(2, 9, 7, 22, fill="#9bc4c0", width=0)
    cv_logo.create_rectangle(10, 2, 15, 22, fill="#ffffff", width=0)
    cv_logo.create_rectangle(18, 6, 23, 22, fill=MAU_NHAN, width=0)

    # Cụm chữ Eyebrow + Tiêu đề
    khung_chu = tk.Frame(noi_dung, bg=MAU_CHINH)
    khung_chu.pack(side="left", fill="y")
    tk.Label(khung_chu, text=eyebrow.upper(), bg=MAU_CHINH, fg="#a9d1cd",
             font=FONT_EYEBROW, anchor="w").pack(anchor="w")
    tk.Label(khung_chu, text=tieu_de, bg=MAU_CHINH, fg="white",
             font=("Segoe UI", 14, "bold"), anchor="w").pack(anchor="w", pady=(2, 0))

    # Huy hiệu bên phải (VD: "CV", "DA") giống .task-badge trong Figma
    if badge_text:
        badge = ctk.CTkFrame(noi_dung, width=38, height=38, corner_radius=9,
                             fg_color="#25766e", border_width=1, border_color="#48938b")
        badge.pack(side="right")
        badge.pack_propagate(False)
        tk.Label(badge, text=badge_text, bg="#25766e", fg=MAU_NHAN,
                 font=("Segoe UI", 10, "bold")).place(relx=0.5, rely=0.5, anchor="center")

    return header
