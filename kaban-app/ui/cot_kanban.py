"""Custom Widget CotKanban: một cột bo góc của bảng Kanban, có thanh cuộn dọc."""
import tkinter as tk
import weakref
from tkinter import ttk
import customtkinter as ctk

from ui import theme
from ui.task_card import TaskCard

# Danh sách các cột đang tồn tại (WeakSet: cột bị huỷ thì tự biến mất khỏi danh sách)
_cac_cot = weakref.WeakSet()

MAU_DAU_COT = {
    "Cần làm": "#64748b",
    "Đang làm": "#176b63",
    "Kiểm tra": "#e9a23b",
    "Hoàn thành": "#2f9e66",
}


def _cuon_toan_cuc(event):
    """Tìm cột đang nằm dưới con trỏ chuột rồi cuộn cột đó."""
    for cot in list(_cac_cot):
        if cot.winfo_exists() and cot.chua_diem(event.x_root, event.y_root):
            cot.cuon(event)
            break


class CotKanban(ctk.CTkFrame):
    """
    Một cột (ví dụ "Đang làm"), KẾ THỪA từ ctk.CTkFrame (tk.Frame bo góc).
    Cấu trúc: tiêu đề + huy hiệu số lượng + Canvas có Scrollbar chứa danh sách TaskCard.
    """

    def __init__(self, master, ten_cot, khi_chon=None, khi_mo=None, khi_menu=None,
                 khi_keo=None, khi_tha=None):
        super().__init__(
            master,
            fg_color=theme.MAU_COT,
            corner_radius=12,
            border_width=1,
            border_color=theme.MAU_VIEN
        )
        self.ten_cot = ten_cot
        self.khi_chon = khi_chon
        self.khi_mo = khi_mo
        self.khi_menu = khi_menu
        self.khi_keo = khi_keo
        self.khi_tha = khi_tha
        self.cac_the = {}            # {ma_cong_viec: TaskCard}

        self._dung_giao_dien()
        self.dat_so_luong(0)
        self._bat_cuon_chuot()

    # ---------------------------------------------------------------- dựng giao diện
    def _dung_giao_dien(self):
        mau_cot = MAU_DAU_COT.get(self.ten_cot, theme.MAU_CHINH)

        # Thanh tiêu đề cột
        self.khung_dau = tk.Frame(self, bg=theme.MAU_COT)
        self.khung_dau.pack(fill="x", padx=12, pady=(10, 6))

        # Chấm màu trạng thái cột
        self.cham_mau = ctk.CTkFrame(self.khung_dau, width=10, height=10,
                                     corner_radius=5, fg_color=mau_cot)
        self.cham_mau.pack(side="left", padx=(0, 8))

        self.lbl_tieu_de = tk.Label(
            self.khung_dau, text=self.ten_cot.upper(),
            bg=theme.MAU_COT, fg=theme.MAU_CHU,
            font=("Segoe UI", 10, "bold"), anchor="w"
        )
        self.lbl_tieu_de.pack(side="left")

        self.lbl_so_luong = ctk.CTkLabel(
            self.khung_dau, text="0", width=26, height=22,
            corner_radius=6, fg_color=theme.MAU_THE,
            text_color=theme.MAU_CHU_NHAN, font=("Segoe UI", 10, "bold")
        )
        self.lbl_so_luong.pack(side="right")

        self.vung = tk.Frame(self, bg=theme.MAU_COT)
        self.vung.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        self.thanh_cuon = ttk.Scrollbar(self.vung, orient="vertical")
        self.thanh_cuon.pack(side="right", fill="y", padx=(0, 2))

        self.canvas = tk.Canvas(
            self.vung, bg=theme.MAU_COT, highlightthickness=0, width=250,
            yscrollcommand=self.thanh_cuon.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.thanh_cuon.configure(command=self.canvas.yview)

        # Frame bên trong Canvas: nơi thật sự chứa các thẻ
        self.ben_trong = tk.Frame(self.canvas, bg=theme.MAU_COT)
        self._cua_so_trong = self.canvas.create_window((0, 0), window=self.ben_trong, anchor="nw")

        self.ben_trong.bind("<Configure>", self._cap_nhat_vung_cuon)
        self.canvas.bind("<Configure>", self._khi_canvas_doi_kich_thuoc)

        self.lbl_trong = tk.Label(
            self.ben_trong, text="Chưa có công việc",
            bg=theme.MAU_COT, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO
        )

    def _cap_nhat_vung_cuon(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _khi_canvas_doi_kich_thuoc(self, event):
        self.canvas.itemconfigure(self._cua_so_trong, width=event.width)

    # ---------------------------------------------------------------- dữ liệu
    def dat_so_luong(self, so_luong):
        self.lbl_tieu_de.configure(text=self.ten_cot.upper())
        self.lbl_so_luong.configure(text=str(so_luong))

    def xoa_het(self):
        for the in self.cac_the.values():
            the.destroy()
        self.cac_the.clear()

    def hien_thi(self, danh_sach_cong_viec):
        """Vẽ lại cột từ danh sách công việc (lấy từ backend)."""
        self.xoa_het()
        for cv in danh_sach_cong_viec:
            the = TaskCard(
                self.ben_trong, cv,
                khi_chon=self.khi_chon,
                khi_mo=self.khi_mo,
                khi_menu=self.khi_menu,
                khi_keo=self.khi_keo,
                khi_tha=self.khi_tha
            )
            the.pack(fill="x", padx=6, pady=5)
            self.cac_the[cv.ma_cong_viec] = the

        if self.cac_the:
            self.lbl_trong.pack_forget()
        else:
            self.lbl_trong.pack(pady=24)
        self.dat_so_luong(len(self.cac_the))
        self.canvas.yview_moveto(0)

    def chua_diem(self, x_root, y_root):
        """True nếu điểm (tọa độ trên màn hình) nằm trong cột này. Dùng cho kéo thả."""
        x, y = self.winfo_rootx(), self.winfo_rooty()
        return x <= x_root < x + self.winfo_width() and y <= y_root < y + self.winfo_height()

    def to_sang(self, bat):
        """Tô sáng cả cột khi đang rê thẻ vào (báo hiệu cột đích)."""
        mau = theme.MAU_COT_SANG if bat else theme.MAU_COT
        vien = theme.MAU_CHINH if bat else theme.MAU_VIEN
        self.configure(fg_color=mau, border_color=vien, border_width=2 if bat else 1)
        for w in (self.khung_dau, self.lbl_tieu_de, self.vung,
                  self.canvas, self.ben_trong, self.lbl_trong):
            w.configure(bg=mau)

    # ---------------------------------------------------------------- cuộn bằng chuột
    def _bat_cuon_chuot(self):
        _cac_cot.add(self)
        if not self.canvas.bind_all("<MouseWheel>"):
            self.canvas.bind_all("<MouseWheel>", _cuon_toan_cuc)
            self.canvas.bind_all("<Button-4>", _cuon_toan_cuc)
            self.canvas.bind_all("<Button-5>", _cuon_toan_cuc)

    def cuon(self, event):
        if self.ben_trong.winfo_reqheight() <= self.canvas.winfo_height():
            return
        if event.num == 4:
            buoc = -1
        elif event.num == 5:
            buoc = 1
        else:
            buoc = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(buoc, "units")
