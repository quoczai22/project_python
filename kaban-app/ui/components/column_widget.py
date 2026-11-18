"""ColumnWidget: Khung một cột trạng thái Kanban bo góc phẳng, hỗ trợ cuộn mượt mà."""
import tkinter as tk
import weakref
from tkinter import ttk
import customtkinter as ctk
from logger import logger
from ui.styles import theme
from ui.components.task_card import TaskCard

_cac_cot = weakref.WeakSet()
_cot_hover_hien_tai = None
_da_dang_ky_cuon = False


def _cuon_toan_cuc(event):
    """Tìm cột đang nằm dưới con trỏ chuột rồi cuộn cột đó với tốc độ mượt mà."""
    if _cot_hover_hien_tai and _cot_hover_hien_tai.winfo_exists():
        _cot_hover_hien_tai.cuon(event)
        return
    for cot in list(_cac_cot):
        if cot.winfo_exists() and cot.chua_diem(event.x_root, event.y_root):
            cot.cuon(event)
            break


def _dang_ky_cuon_toan_cuc(widget):
    """Chỉ gắn sự kiện cuộn chuột toàn cục đúng một lần cho cả ứng dụng."""
    global _da_dang_ky_cuon
    if _da_dang_ky_cuon:
        return
    for su_kien in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        widget.bind_all(su_kien, _cuon_toan_cuc, add="+")
    _da_dang_ky_cuon = True


GIOI_HAN_WIP = {
    "Đang làm": 4,
    "Kiểm tra": 3,
}


class ColumnWidget(ctk.CTkFrame):
    """
    Khung một cột trạng thái trên bảng Kanban:
    - Tiêu đề cột phẳng dạng pill pastel thanh lịch: chấm trạng thái + tên + số lượng + nút '+'.
    - Vùng danh sách thẻ công việc hỗ trợ cuộn dọc mượt mà.
    - Trạng thái rỗng (empty state) tối giản.
    """

    def __init__(self, master, ten_cot, ten_nguoi_map=None,
                 khi_chon=None, khi_mo=None, khi_menu=None,
                 khi_keo=None, khi_tha=None, khi_them_nhanh=None,
                 khi_chuyen_nhanh=None):
        super().__init__(
            master,
            fg_color=theme.MAU_COT,
            corner_radius=0,
            border_width=1,
            border_color=theme.MAU_VIEN_COT
        )
        self.ten_cot = ten_cot
        self.ten_nguoi_map = ten_nguoi_map or {}
        self.khi_chon = khi_chon
        self.khi_mo = khi_mo
        self.khi_menu = khi_menu
        self.khi_keo = khi_keo
        self.khi_tha = khi_tha
        self.khi_them_nhanh = khi_them_nhanh
        self.khi_chuyen_nhanh = khi_chuyen_nhanh
        self.cac_the = {}  # {ma_cong_viec: TaskCard}

        self._dung_giao_dien()
        self.dat_so_luong(0)
        self._bat_cuon_chuot()

    def _dung_giao_dien(self):
        """Khởi tạo toàn bộ giao diện tiêu đề, thân cột và thanh cuộn."""
        info_pastel = theme.MAU_COT_PASTEL.get(self.ten_cot, {
            "nen_header": theme.MAU_THE,
            "vien_header": theme.MAU_VIEN,
            "dot": theme.MAU_CHINH,
            "chu": theme.MAU_CHU,
            "nen_so": theme.MAU_O_NHAP,
        })
        mau_cot = info_pastel["dot"]
        nen_header = info_pastel["nen_header"]
        vien_header = info_pastel["vien_header"]
        mau_chu_tieu_de = info_pastel["chu"]
        nen_so = info_pastel["nen_so"]

        # Header cột
        self.khung_dau = ctk.CTkFrame(
            self, fg_color=nen_header, corner_radius=0,
            border_width=1, border_color=vien_header
        )
        self.khung_dau.pack(fill="x", padx=4, pady=(6, 4))

        noi_dung_dau = tk.Frame(self.khung_dau, bg=nen_header)
        noi_dung_dau.pack(fill="x", padx=6, pady=6)

        self.cham_mau = ctk.CTkFrame(
            noi_dung_dau, width=8, height=8, corner_radius=0,
            fg_color=mau_cot, bg_color=nen_header
        )
        self.cham_mau.pack(side="left", padx=(0, 6))

        self.lbl_tieu_de = tk.Label(
            noi_dung_dau, text=self.ten_cot,
            bg=nen_header, fg=mau_chu_tieu_de,
            font=theme.FONT_DAM, anchor="w"
        )
        self.lbl_tieu_de.pack(side="left")

        if self.khi_them_nhanh is not None:
            self.btn_them_nhanh = ctk.CTkButton(
                noi_dung_dau, text="+",
                command=lambda: self.khi_them_nhanh(self.ten_cot),
                width=22, height=22, corner_radius=0,
                fg_color=vien_header, hover_color="#cbd5e1",
                border_width=0, text_color=mau_chu_tieu_de,
                bg_color=nen_header, font=theme.FONT_DAM
            )
            self.btn_them_nhanh.pack(side="right", padx=(4, 0))
        else:
            self.btn_them_nhanh = None

        self.lbl_so_luong = ctk.CTkLabel(
            noi_dung_dau, text="0", width=28, height=22,
            corner_radius=0, fg_color=nen_so, text_color=mau_chu_tieu_de,
            bg_color=nen_header, font=theme.FONT_NHO_DAM
        )
        self.lbl_so_luong.pack(side="right")

        self.lbl_canh_bao_cot = ctk.CTkLabel(
            noi_dung_dau, text="", height=20, corner_radius=0, padx=4,
            fg_color=theme.MAU_NEN_LOI_NHAT, text_color=theme.MAU_LOI,
            bg_color=nen_header, font=theme.FONT_NHO_DAM
        )

        if self.khi_them_nhanh is not None:
            self.btn_them_duoi = ctk.CTkButton(
                self, text="+ Thêm thẻ",
                command=lambda: self.khi_them_nhanh(self.ten_cot),
                height=26, corner_radius=0,
                fg_color="#d2dde7", hover_color="#c1cfd9",
                border_width=0, text_color=theme.MAU_CHU_NHAN,
                bg_color=theme.MAU_COT, font=theme.FONT_NHO_DAM
            )
            self.btn_them_duoi.pack(side="bottom", fill="x", padx=6, pady=(2, 6))
        else:
            self.btn_them_duoi = None

        # Vùng cuộn công việc
        self.vung = tk.Frame(self, bg=theme.MAU_COT)
        self.vung.pack(fill="both", expand=True, padx=3, pady=(0, 3))

        self.canvas = tk.Canvas(
            self.vung, bg=theme.MAU_COT, highlightthickness=0, width=150
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        self.thanh_cuon = ttk.Scrollbar(self.vung, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.thanh_cuon.set)

        self.ben_trong = tk.Frame(self.canvas, bg=theme.MAU_COT)
        self._cua_so_trong = self.canvas.create_window(
            (0, 0), window=self.ben_trong, anchor="nw"
        )

        self.ben_trong.bind("<Configure>", self._cap_nhat_vung_cuon)
        self.canvas.bind("<Configure>", self._khi_canvas_doi_kich_thuoc)

        # Trạng thái rỗng (empty-state)
        self.khung_trong = ctk.CTkFrame(
            self.ben_trong, fg_color="#e8eff5", corner_radius=0,
            border_width=0
        )
        self.lbl_trong = tk.Label(
            self.khung_trong, text="Chưa có công việc",
            bg="#e8eff5", fg=theme.MAU_CHU_NHAN, font=theme.FONT_NHO_DAM
        )
        self.lbl_trong.pack(pady=(16, 2), padx=12)
        self.lbl_trong_goi_y = tk.Label(
            self.khung_trong,
            text="Kéo thẻ vào đây hoặc thêm việc mới",
            bg="#e8eff5", fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO,
            wraplength=200
        )
        self.lbl_trong_goi_y.pack(pady=(0, 10), padx=12)

        if self.khi_them_nhanh is not None:
            self.btn_trong_them = ctk.CTkButton(
                self.khung_trong, text="+ Thêm vào cột",
                command=lambda: self.khi_them_nhanh(self.ten_cot),
                height=26, corner_radius=0,
                fg_color=theme.MAU_THE, hover_color=theme.MAU_CHINH_NHAT,
                border_width=1, border_color=theme.MAU_VIEN_COT,
                text_color=theme.MAU_CHINH_DAM, font=theme.FONT_NHO_DAM
            )
            self.btn_trong_them.pack(pady=(0, 14), padx=14)
        else:
            self.btn_trong_them = None

    def _cap_nhat_vung_cuon(self, _event=None):
        """Cập nhật vùng cuộn; cột ít thẻ thì không trượt được, chỉ hiện scrollbar khi tràn."""
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        cao_canvas = self.canvas.winfo_height()
        # Vùng cuộn không bao giờ thấp hơn canvas, nên nội dung luôn dính mép trên
        self.canvas.configure(scrollregion=(0, 0, bbox[2], max(bbox[3], cao_canvas)))
        can_cuon = (
            self.ben_trong.winfo_reqheight() > cao_canvas
            and cao_canvas > 60
        )
        if can_cuon:
            if not self.thanh_cuon.winfo_ismapped():
                self.thanh_cuon.pack(side="right", fill="y", padx=(0, 2))
        else:
            if self.thanh_cuon.winfo_ismapped():
                self.thanh_cuon.pack_forget()

    def _khi_canvas_doi_kich_thuoc(self, event):
        """Khớp chiều rộng nội dung bên trong canvas khi canvas đổi cỡ."""
        self.canvas.itemconfigure(self._cua_so_trong, width=event.width)
        self._cap_nhat_vung_cuon()

    def cap_nhat_nguoi_dung(self, ten_nguoi_map):
        """Cập nhật bản đồ tên người dùng."""
        self.ten_nguoi_map = ten_nguoi_map or {}

    def dat_so_luong(self, so_luong):
        """Cập nhật nhãn số lượng trên đầu cột."""
        self.lbl_tieu_de.configure(text=self.ten_cot)
        self.lbl_so_luong.configure(text=str(so_luong))

    def xoa_het(self):
        """Xóa toàn bộ các thẻ công việc hiện có trong cột."""
        for the in self.cac_the.values():
            the.destroy()
        self.cac_the.clear()

    def hien_thi(self, danh_sach_cong_viec):
        """Vẽ lại cột từ danh sách công việc."""
        self.xoa_het()
        for cv in danh_sach_cong_viec:
            the = TaskCard(
                self.ben_trong, cv,
                ten_nguoi_map=self.ten_nguoi_map,
                khi_chon=self.khi_chon,
                khi_mo=self.khi_mo,
                khi_menu=self.khi_menu,
                khi_keo=self.khi_keo,
                khi_tha=self.khi_tha,
                khi_chuyen_nhanh=self.khi_chuyen_nhanh
            )
            the.pack(fill="x", padx=6, pady=5)
            self.cac_the[cv.ma_cong_viec] = the

        if self.cac_the:
            self.khung_trong.pack_forget()
        else:
            self.khung_trong.pack(fill="x", padx=10, pady=16)

        wip = GIOI_HAN_WIP.get(self.ten_cot, 0)
        vuot_wip = wip > 0 and len(danh_sach_cong_viec) > wip
        so_can_chu_y = sum(1 for cv in danh_sach_cong_viec if cv.can_chu_y())
        if vuot_wip and so_can_chu_y > 0:
            self.lbl_canh_bao_cot.configure(text=f"WIP • {so_can_chu_y} trễ")
            self.lbl_canh_bao_cot.pack(side="right", padx=(0, 4))
        elif vuot_wip:
            self.lbl_canh_bao_cot.configure(text="Quá WIP")
            self.lbl_canh_bao_cot.pack(side="right", padx=(0, 4))
        elif so_can_chu_y > 0:
            self.lbl_canh_bao_cot.configure(text=f"{so_can_chu_y} trễ")
            self.lbl_canh_bao_cot.pack(side="right", padx=(0, 4))
        else:
            self.lbl_canh_bao_cot.pack_forget()

        if wip > 0:
            self.dat_so_luong(f"{len(self.cac_the)}/{wip}")
        else:
            self.dat_so_luong(len(self.cac_the))
        self.canvas.yview_moveto(0)

    def chua_diem(self, x_root, y_root):
        """Kiểm tra xem tọa độ màn hình có nằm trong cột không."""
        x, y = self.winfo_rootx(), self.winfo_rooty()
        return x <= x_root < x + self.winfo_width() and y <= y_root < y + self.winfo_height()

    def to_sang(self, bat):
        """Tô sáng cột khi kéo thả thẻ công việc vào."""
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        mau = theme.MAU_COT_SANG if bat else theme.MAU_COT
        vien = theme.MAU_CHINH if bat else theme.MAU_VIEN_COT
        mau_trong = mau if bat else "#e8eff5"
        try:
            self.configure(fg_color=mau, border_color=vien, border_width=2 if bat else 1)
        except Exception:
            pass
        try:
            self.khung_trong.configure(fg_color=mau_trong)
        except Exception:
            pass
        if self.btn_them_duoi is not None:
            try:
                self.btn_them_duoi.configure(bg_color=mau)
            except Exception:
                pass
        # Chỉ cập nhật canvas và vung, không cập nhật ben_trong vì CustomTkinter
        # sẽ đệ quy configure lên tất cả TaskCard con gây ra lỗi TclError khi thẻ bị hủy
        for w in (self.vung, self.canvas):
            try:
                if w.winfo_exists():
                    w.configure(bg=mau)
            except Exception:
                pass
        for w_trong in (self.lbl_trong, self.lbl_trong_goi_y):
            try:
                if w_trong.winfo_exists():
                    w_trong.configure(bg=mau_trong)
            except Exception:
                pass
        if self.btn_trong_them is not None:
            try:
                self.btn_trong_them.configure(bg_color=mau_trong)
            except Exception:
                pass

    def _bat_cuon_chuot(self):
        """Kích hoạt sự kiện lắng nghe cuộn chuột trên cột."""
        _cac_cot.add(self)
        self.bind("<Enter>", lambda _e: self._set_hover(True), add="+")
        self.bind("<Leave>", lambda _e: self._set_hover(False), add="+")
        self.canvas.bind("<Enter>", lambda _e: self._set_hover(True), add="+")
        self.canvas.bind("<Leave>", lambda _e: self._set_hover(False), add="+")
        self.ben_trong.bind("<Enter>", lambda _e: self._set_hover(True), add="+")
        self.ben_trong.bind("<Leave>", lambda _e: self._set_hover(False), add="+")
        _dang_ky_cuon_toan_cuc(self.canvas)

    def _set_hover(self, bat):
        global _cot_hover_hien_tai
        if bat:
            _cot_hover_hien_tai = self
        elif _cot_hover_hien_tai is self:
            _cot_hover_hien_tai = None

    def cuon(self, event):
        """Cuộn nội dung trong cột với tốc độ tự nhiên, không giật lag."""
        if event.num == 4:
            buoc = -3
        elif event.num == 5:
            buoc = 3
        elif getattr(event, "delta", 0):
            # touchpad hay gửi delta nhỏ (<30) nên luôn cuộn ít nhất 1 nấc
            buoc = -int(event.delta / 30) or (-1 if event.delta > 0 else 1)
        else:
            return
        try:
            self.canvas.yview_scroll(buoc, "units")
        except tk.TclError:
            logger.debug("Canvas đã bị hủy khi đang cuộn")


# Alias tương thích ngược
CotKanban = ColumnWidget