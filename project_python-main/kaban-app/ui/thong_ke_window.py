"""Cửa sổ thống kê: biểu đồ cột vẽ bằng Canvas + bảng cảnh báo bằng Treeview."""
import math
import tkinter as tk
from tkinter import ttk

from ui import theme
from ui.tien_ich import can_giua

# Màu cột biểu đồ theo tên cột Kanban (cột lạ thì dùng màu chính)
MAU_COT_BIEU_DO = {
    "Cần làm": "#95a5a6",
    "Đang làm": "#2f6fed",
    "Kiểm tra": "#f1c40f",
    "Hoàn thành": "#27ae60",
}


class ThongKeWindow(tk.Toplevel):
    def __init__(self, master, du_an):
        super().__init__(master)
        self.du_an = du_an
        self.so_lieu = {}              # {ten_cot: so_viec}

        self.title("Thống kê dự án")
        self.configure(bg=theme.MAU_NEN)
        self.minsize(680, 540)

        self.var_chua_xong = tk.BooleanVar(value=True)

        style = ttk.Style()
        style.configure("Treeview", rowheight=26, font=theme.FONT_CHUAN)
        style.configure("Treeview.Heading", font=theme.FONT_DAM)

        self._dung_giao_dien()
        can_giua(self, 840, 660)
        self.cap_nhat()

    # ------------------------------------------------------------ giao diện
    def _dung_giao_dien(self):
        # Vùng 1: tiêu đề + thanh tiến độ
        dau = ttk.Frame(self, padding=(14, 10))
        dau.pack(fill="x")
        self.lbl_tien_do = ttk.Label(dau, font=theme.FONT_DAM)
        self.lbl_tien_do.pack(anchor="w")
        self.thanh_tien_do = ttk.Progressbar(dau, maximum=100, mode="determinate")
        self.thanh_tien_do.pack(fill="x", pady=(6, 0))

        # Vùng 2: biểu đồ cột (Canvas), vẽ lại mỗi khi cửa sổ đổi kích thước
        self.canvas = tk.Canvas(self, bg=theme.MAU_THE, height=260,
                                highlightthickness=1,
                                highlightbackground=theme.MAU_VIEN_THE)
        self.canvas.pack(fill="both", expand=True, padx=14)
        self.canvas.bind("<Configure>", self.ve_bieu_do)

        # Vùng 3: bảng cảnh báo (Treeview + Scrollbar), chỉ dùng grid
        duoi = ttk.Frame(self, padding=(14, 10, 14, 12))
        duoi.pack(fill="both", expand=True)
        duoi.columnconfigure(0, weight=1)
        duoi.rowconfigure(1, weight=1)

        ttk.Label(duoi, text="Cảnh báo hạn công việc",
                  font=theme.FONT_DAM).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Checkbutton(duoi, text="Chỉ hiện việc chưa hoàn thành",
                        variable=self.var_chua_xong,
                        command=self._nap_canh_bao).grid(row=0, column=1, sticky="e")

        cac_cot = (("ma", "Mã", 80, "center"),
                   ("tieu_de", "Tiêu đề", 260, "w"),
                   ("loai", "Loại", 120, "w"),
                   ("canh_bao", "Cảnh báo", 280, "w"))
        self.tree = ttk.Treeview(duoi, columns=[c[0] for c in cac_cot],
                                 show="headings", height=8, selectmode="browse")
        for khoa, tieu_de, rong, can in cac_cot:
            self.tree.heading(khoa, text=tieu_de)
            self.tree.column(khoa, width=rong, anchor=can)
        self.tree.tag_configure("qua_han", foreground=theme.MAU_LOI)
        self.tree.tag_configure("khan", foreground=theme.MAU_CANH_BAO)

        thanh = ttk.Scrollbar(duoi, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=thanh.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        thanh.grid(row=1, column=1, sticky="ns")

    # ------------------------------------------------------------ dữ liệu
    def dat_du_an(self, du_an):
        """Cửa sổ chính gọi khi dữ liệu / dự án đổi."""
        self.du_an = du_an
        self.cap_nhat()

    def cap_nhat(self):
        da = self.du_an
        self.so_lieu = {ten: 0 for ten in da.danh_sach_cot}
        for cv in da.cong_viec:
            if cv.trang_thai in self.so_lieu:
                self.so_lieu[cv.trang_thai] += 1

        tong = len(da.cong_viec)
        xong = sum(1 for cv in da.cong_viec if cv.is_hoan_thanh())
        tien_do = da.tinh_tien_do()
        self.title(f"Thống kê - {da.ten_du_an}")
        self.lbl_tien_do.configure(
            text=f"Tiến độ hoàn thành: {tien_do}%   ({xong}/{tong} việc)")
        self.thanh_tien_do["value"] = tien_do

        self.ve_bieu_do()
        self._nap_canh_bao()

    def _nap_canh_bao(self):
        """Đổ danh sách cảnh báo (đa hình canh_bao() của từng loại việc) vào Treeview."""
        self.tree.delete(*self.tree.get_children())
        dong = []
        for muc in self.du_an.lay_danh_sach_canh_bao():
            cv = self.du_an.tim_cong_viec_theo_ma(muc["ma_cong_viec"])
            if self.var_chua_xong.get() and cv is not None and cv.is_hoan_thanh():
                continue
            chu = muc["canh_bao"].upper()
            if "QUÁ HẠN" in chu:
                hang, tag = 0, "qua_han"
            elif "KHẨN CẤP" in chu or "CẢNH BÁO ĐỎ" in chu:
                hang, tag = 1, "khan"
            else:
                hang, tag = 2, ""
            dong.append((hang, (muc["ma_cong_viec"], muc["tieu_de"],
                                muc["loai"], muc["canh_bao"]), tag))

        dong.sort(key=lambda d: d[0])            # quá hạn lên đầu
        if not dong:
            self.tree.insert("", "end", values=("", "Không có công việc cần cảnh báo", "", ""))
        for _, gia_tri, tag in dong:
            self.tree.insert("", "end", values=gia_tri, tags=(tag,) if tag else ())

    # ------------------------------------------------------------ vẽ biểu đồ
    def ve_bieu_do(self, event=None):
        c = self.canvas
        c.delete("all")
        rong, cao = c.winfo_width(), c.winfo_height()
        if rong < 120 or cao < 120 or not self.so_lieu:
            return

        le_trai, le_phai, le_tren, le_duoi = 44, 24, 44, 44
        day = cao - le_duoi
        vung_cao = day - le_tren
        cao_nhat = max(max(self.so_lieu.values()), 1)
        buoc = max(1, math.ceil(cao_nhat / 5))

        c.create_text(rong // 2, 20, text="Số công việc theo cột",
                      font=theme.FONT_DAM, fill=theme.MAU_CHU)

        # Đường lưới ngang + nhãn trục tung
        for v in range(0, cao_nhat + 1, buoc):
            y = day - v / cao_nhat * vung_cao
            c.create_line(le_trai, y, rong - le_phai, y, fill=theme.MAU_COT)
            c.create_text(le_trai - 8, y, text=str(v), anchor="e",
                          font=theme.FONT_NHO, fill=theme.MAU_CHU_PHU)

        # Các cột
        o_rong = (rong - le_trai - le_phai) / len(self.so_lieu)
        cot_rong = min(o_rong * 0.55, 90)
        for i, (ten, so) in enumerate(self.so_lieu.items()):
            x0 = le_trai + i * o_rong + (o_rong - cot_rong) / 2
            x1 = x0 + cot_rong
            y0 = day - so / cao_nhat * vung_cao
            mau = MAU_COT_BIEU_DO.get(ten, theme.MAU_CHINH)
            c.create_rectangle(x0, y0, x1, day, fill=mau, outline="")
            c.create_text((x0 + x1) / 2, y0 - 10, text=str(so),
                          font=theme.FONT_DAM, fill=theme.MAU_CHU)
            c.create_text((x0 + x1) / 2, day + 18, text=ten,
                          font=theme.FONT_CHUAN, fill=theme.MAU_CHU)

        c.create_line(le_trai, day, rong - le_phai, day, fill=theme.MAU_CHU_PHU)