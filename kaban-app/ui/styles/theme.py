"""Quản lý giao diện, bảng mã màu và kiểu dáng tập trung (Flat 100%, Corner Radius = 0)."""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from logger import logger
from ui.styles.fonts import (
    FONT_FAMILY, font_family, FONT_TIEU_DE, FONT_CHAO_MUNG,
    FONT_PHU_DE, FONT_CHUAN, FONT_DAM, FONT_NHO, FONT_NHO_DAM, FONT_KPI
)

# Bảng màu chủ đạo theo Palette người dùng (Lavender & Periwinkle Workspace)
# Các mã màu gốc từ ảnh: #a6a2c3, #d2d1df, #e0e0ec, #a0a6c6, #a9b3d7
MAU_PALETTE_1 = "#a6a2c3"       # Lavender Slate
MAU_PALETTE_2 = "#d2d1df"       # Soft Lavender Gray
MAU_PALETTE_3 = "#e0e0ec"       # Whisper Lilac
MAU_PALETTE_4 = "#a0a6c6"       # Periwinkle Muted
MAU_PALETTE_5 = "#a9b3d7"       # Soft Blue-Lavender

MAU_NEN = "#f4f3f8"            # Nền ứng dụng theo tông Whisper Lilac dịu mắt
MAU_CHINH = "#6d669b"          # Tím Lavender đậm đạt chuẩn tương phản AA (>4.5:1)
MAU_CHINH_DAM = "#5a5386"      # Hover tím đậm
MAU_CHINH_NHAT = "#e9e8f4"     # Nền pastel active (dẫn xuất từ #e0e0ec)
MAU_NHAN = "#8e88bd"           # Lavender sáng

MAU_CHU = "#1e1b33"            # Chữ chính tím than đậm tương phản cực cao (>12:1)
MAU_CHU_NHAN = "#38344e"       # Chữ nhãn form / phụ đề
MAU_CHU_PHU = "#5c5875"        # Chữ phụ đạt chuẩn WCAG AA
MAU_PLACEHOLDER = "#8a86a2"    # Placeholder
MAU_THE = "#ffffff"            # Nền thẻ trắng tinh khôi
MAU_O_NHAP = "#faf9fc"         # Nền ô nhập liệu
MAU_O_NHAP_KHOA = "#edeef6"    # Nền ô nhập bị khóa
MAU_COT = "#e7e6f0"            # Nền khay cột Kanban theo tông #e0e0ec
MAU_COT_SANG = "#dedde9"       # Nền cột khi hover
MAU_VIEN = "#d2d1df"           # Viền chuẩn từ cột 1 của Palette
MAU_VIEN_COT = "#c7c5d7"       # Viền khay cột
MAU_VIEN_THE = "#d2d1df"       # Viền thẻ / control chuẩn #d2d1df
MAU_VIEN_HOVER = "#8e88bd"     # Viền nổi bật hover
MAU_THE_HOVER = "#faf9fc"      # Nền thẻ khi rê chuột

MAU_LOI = "#e11d48"            # Rose-red cảnh báo / lỗi
MAU_NEN_LOI_NHAT = "#ffe4e6"   # Nền đỏ hồng nhạt
MAU_HOAN_THANH = "#15803d"     # Xanh lá hoàn thành
MAU_CANH_BAO = "#b45309"       # Hổ phách đậm cảnh báo
MAU_DISABLED_NEN = "#e2e8f0"   # Nền nút disabled
MAU_DISABLED_CHU = "#8a86a2"   # Chữ disabled rõ đọc
MAU_HEADER_SUB = "#e0e0ec"     # Chữ phụ trên header
MAU_BADGE_HEADER_NEN = "#5a5386"
MAU_BADGE_HEADER_CHU = "#fef3c7"

# Màu mức ưu tiên
MAU_UU_TIEN = {
    "Thấp": "#16a34a",
    "Trung bình": "#4f46e5",
    "Cao": "#d97706",
    "Khẩn": "#e11d48",
}

MAU_NEN_BADGE_UU_TIEN = {
    "Thấp": "#dcfce7",
    "Trung bình": "#e0e7ff",
    "Cao": "#fef3c7",
    "Khẩn": "#ffe4e6",
}

MAU_CHU_BADGE_UU_TIEN = {
    "Thấp": "#166534",
    "Trung bình": "#3730a3",
    "Cao": "#92400e",
    "Khẩn": "#9f1239",
}

MAU_CHU_TREN_UU_TIEN = {
    "Thấp": "white",
    "Trung bình": "#1e1b33",
    "Cao": "white",
    "Khẩn": "white",
}

# Màu nhãn phân loại
MAU_NHAN_TAG = {
    "Backend": "#6d669b",
    "Giao diện": "#7c3aed",
    "Lỗi": "#b91c1c",
    "Tài liệu": "#0f766e",
    "Kiểm thử": "#4338ca",
}

MAU_NEN_NHAN_TAG = {
    "Backend": "#e0e7ff",
    "Giao diện": "#ede9fe",
    "Lỗi": "#fee2e2",
    "Tài liệu": "#ccfbf1",
    "Kiểm thử": "#e0e7ff",
}

MAU_CHU_NHAN_TAG = {
    "Backend": "#3730a3",
    "Giao diện": "#5b21b6",
    "Lỗi": "#991b1b",
    "Tài liệu": "#115e59",
    "Kiểm thử": "#3730a3",
}

MAU_TRANG_THAI_COT = {
    "Cần làm": "#64748b",
    "Đang làm": "#6d669b",
    "Kiểm tra": "#d97706",
    "Hoàn thành": "#16a34a",
}

# Bảng màu Pastel cho Header các cột trạng thái Kanban
MAU_COT_PASTEL = {
    "Cần làm": {
        "nen_header": "#f1f5f9",
        "vien_header": "#cbd5e1",
        "dot": "#64748b",
        "chu": "#0f172a",
        "nen_so": "#e2e8f0",
    },
    "Đang làm": {
        "nen_header": "#e9e8f4",
        "vien_header": "#d2d1df",
        "dot": "#6d669b",
        "chu": "#1e1b33",
        "nen_so": "#d2d1df",
    },
    "Kiểm tra": {
        "nen_header": "#fef3c7",
        "vien_header": "#fde68a",
        "dot": "#d97706",
        "chu": "#78350f",
        "nen_so": "#fde68a",
    },
    "Hoàn thành": {
        "nen_header": "#dcfce7",
        "vien_header": "#bbf7d0",
        "dot": "#16a34a",
        "chu": "#14532d",
        "nen_so": "#bbf7d0",
    },
}

# Quy chuẩn phẳng 100% không bo tròn theo yêu cầu người dùng
CORNER_RADIUS = 0
PADDING_THE = 12
PADDING_O_NHAP = 8

# Palette màu avatar thành viên
PALETTE_AVATAR = (
    "#16a34a", "#2563eb", "#d97706", "#7c3aed",
    "#0d9488", "#e11d48", "#475569", "#ea580c"
)

def mau_avatar(ten_dang_nhap: str) -> str:
    """Sinh màu avatar đại diện ngẫu nhiên nhưng cố định theo tên đăng nhập."""
    if not ten_dang_nhap:
        return PALETTE_AVATAR[0]
    chi_so = sum(ord(c) for c in ten_dang_nhap) % len(PALETTE_AVATAR)
    return PALETTE_AVATAR[chi_so]

def ap_dung_style():
    """Áp dụng theme cho CustomTkinter và ttk."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        logger.warning("Không có theme 'clam', dùng theme mặc định của ttk")

    style.configure(
        "Treeview",
        background=MAU_THE,
        foreground=MAU_CHU,
        fieldbackground=MAU_THE,
        rowheight=32,
        font=FONT_CHUAN,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=MAU_COT,
        foreground=MAU_CHU,
        font=FONT_NHO_DAM,
        relief="flat",
        borderwidth=1
    )
    style.map(
        "Treeview",
        background=[("selected", MAU_CHINH_NHAT)],
        foreground=[("selected", MAU_CHINH_DAM)]
    )
    style.map(
        "Treeview.Heading",
        background=[("active", MAU_COT_SANG)]
    )

def tao_nut(master, text, command=None, loai="chinh", **kwargs):
    """Tạo nút chuẩn phẳng corner_radius=0."""
    cau_hinh = {
        "corner_radius": CORNER_RADIUS,
        "font": FONT_DAM,
        "height": 36,
        "border_width": 0,
    }
    if loai == "chinh":
        cau_hinh.update({
            "fg_color": MAU_CHINH,
            "hover_color": MAU_CHINH_DAM,
            "text_color": "white",
        })
    elif loai == "phu":
        cau_hinh.update({
            "fg_color": MAU_THE,
            "hover_color": MAU_THE_HOVER,
            "text_color": MAU_CHU,
            "border_width": 1,
            "border_color": MAU_VIEN_THE,
        })
    elif loai == "xoa":
        cau_hinh.update({
            "fg_color": MAU_NEN_LOI_NHAT,
            "hover_color": "#fecdd3",
            "text_color": MAU_LOI,
            "border_width": 1,
            "border_color": "#fecdd3",
        })
    cau_hinh.update(kwargs)
    return ctk.CTkButton(master, text=text, command=command, **cau_hinh)

def tao_entry(master, placeholder="", cao=34, an_chu=False, show=None, **kwargs):
    """Tạo ô nhập văn bản phẳng corner_radius=0, hỗ trợ an_chu/show để ẩn mật khẩu."""
    ch = {
        "corner_radius": CORNER_RADIUS,
        "font": FONT_CHUAN,
        "height": cao,
        "fg_color": MAU_O_NHAP,
        "border_color": MAU_VIEN,
        "border_width": 1,
        "text_color": MAU_CHU,
        "placeholder_text_color": MAU_PLACEHOLDER,
    }
    if placeholder:
        ch["placeholder_text"] = placeholder

    an_chu_val = kwargs.pop("an_chu", an_chu)
    show_val = kwargs.pop("show", show)
    if show_val is not None:
        ch["show"] = show_val
    elif an_chu_val:
        ch["show"] = "*"

    ch.update(kwargs)
    try:
        return ctk.CTkEntry(master, **ch)
    except Exception:
        cac_khoa_hop_le = {
            "width", "height", "corner_radius", "border_width", "bg_color", "fg_color",
            "border_color", "text_color", "placeholder_text_color", "textvariable",
            "placeholder_text", "font", "state", "show"
        }
        ch_sach = {k: v for k, v in ch.items() if k in cac_khoa_hop_le}
        return ctk.CTkEntry(master, **ch_sach)

def tao_combobox(master, values=None, **kwargs):
    """Tạo hộp chọn combobox phẳng corner_radius=0."""
    ch = {
        "corner_radius": CORNER_RADIUS,
        "font": FONT_CHUAN,
        "dropdown_font": FONT_CHUAN,
        "height": 34,
        "fg_color": MAU_O_NHAP,
        "border_color": MAU_VIEN,
        "border_width": 1,
        "text_color": MAU_CHU,
        "button_color": MAU_COT,
        "button_hover_color": MAU_COT_SANG,
        "dropdown_fg_color": MAU_THE,
        "dropdown_text_color": MAU_CHU,
        "dropdown_hover_color": MAU_CHINH_NHAT,
        "values": values or [],
    }
    ch.update(kwargs)
    return ctk.CTkComboBox(master, **ch)

def dat_gia_tri_entry(entry, gia_tri: str):
    """Gán giá trị cho ô nhập Entry an toàn, hỗ trợ cả khi Entry đang ở state disabled."""
    trang_thai_cu = "normal"          # gán trước để không bị NameError nếu cget lỗi
    try:
        trang_thai_cu = str(entry.cget("state"))
        if trang_thai_cu == "disabled":
            entry.configure(state="normal")
    except (tk.TclError, ValueError):   # CustomTkinter ném ValueError với thuộc tính không hỗ trợ
        logger.debug("Ô nhập không hỗ trợ thuộc tính 'state'")
    entry.delete(0, tk.END)
    entry.insert(0, gia_tri or "")
    if trang_thai_cu == "disabled":
        try:
            entry.configure(state="disabled")
        except (tk.TclError, ValueError):
            logger.debug("Không khôi phục được trạng thái disabled của ô nhập")

def tao_badge(master, text, bg, fg, **kwargs):
    """Tạo một badge nhãn phẳng corner_radius=0."""
    ch = {
        "corner_radius": CORNER_RADIUS,
        "fg_color": bg,
        "text_color": fg,
        "font": FONT_NHO_DAM,
        "height": 22,
        "padx": 8,
    }
    ch.update(kwargs)
    return ctk.CTkLabel(master, text=text, **ch)

def tao_nut_chinh(master, text, command=None, **kwargs):
    return tao_nut(master, text, command=command, loai="chinh", **kwargs)

def tao_nut_phu(master, text, command=None, **kwargs):
    return tao_nut(master, text, command=command, loai="phu", **kwargs)

def tao_nut_nguy_hiem(master, text, command=None, **kwargs):
    return tao_nut(master, text, command=command, loai="xoa", **kwargs)

def tao_header_figma(master, tieu_de, badge_text="KB", cao=74, subtitle=""):
    """Header pop-up dạng phẳng chuyên nghiệp chuẩn thiết kế."""
    f = tk.Frame(master, bg=MAU_CHINH, height=cao)
    f.pack(fill="x")
    f.pack_propagate(False)

    box = tk.Frame(f, bg=MAU_CHINH, padx=18, pady=12)
    box.pack(fill="both", expand=True)

    b_badge = tk.Frame(box, bg=MAU_BADGE_HEADER_NEN, width=32, height=32)
    b_badge.pack(side="left", padx=(0, 10))
    b_badge.pack_propagate(False)
    tk.Label(b_badge, text=badge_text, bg=MAU_BADGE_HEADER_NEN, fg=MAU_BADGE_HEADER_CHU, font=FONT_DAM).place(relx=0.5, rely=0.5, anchor="center")

    info = tk.Frame(box, bg=MAU_CHINH)
    info.pack(side="left", fill="both", expand=True)
    tk.Label(info, text=tieu_de, bg=MAU_CHINH, fg="white", font=FONT_DAM, anchor="w").pack(fill="x")
    if subtitle:
        tk.Label(info, text=subtitle, bg=MAU_CHINH, fg=MAU_HEADER_SUB, font=FONT_NHO, anchor="w").pack(fill="x")
    return f
