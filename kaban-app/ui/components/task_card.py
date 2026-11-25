"""Thẻ công việc (TaskCard) nằm bên trong cột Kanban (tái sử dụng nhiều lần)."""
import tkinter as tk
import customtkinter as ctk
from logger import logger
from config import TRANG_THAI_HOP_LE
from ui.styles import theme
from utils.helpers import tao_chu_viet_tat


class TaskCard(ctk.CTkFrame):
    """
    Thẻ công việc, kế thừa từ ctk.CTkFrame:
    - Thẻ nền trắng viền mảnh rõ nét + badge mức ưu tiên nền pastel tương phản cao.
    - Badge nhãn phân loại có màu riêng.
    - Hiển thị mã, tiêu đề, mô tả tóm tắt, người phụ trách, số bình luận và cảnh báo đa hình.
    - Hỗ trợ click chọn, double-click mở sửa, chuột phải mở menu, hover mượt và kéo-thả.
    """

    def __init__(self, master, cong_viec, ten_nguoi_map=None,
                 khi_chon=None, khi_mo=None, khi_menu=None,
                 khi_keo=None, khi_tha=None, khi_chuyen_nhanh=None):
        super().__init__(
            master,
            fg_color=theme.MAU_THE,
            corner_radius=0,
            border_width=1,
            border_color=theme.MAU_VIEN_THE,
            cursor="hand2"
        )
        self.cong_viec = cong_viec
        self.ten_nguoi_map = ten_nguoi_map or {}
        self.khi_chon = khi_chon
        self.khi_mo = khi_mo
        self.khi_menu = khi_menu
        self.khi_keo = khi_keo
        self.khi_tha = khi_tha
        self.khi_chuyen_nhanh = khi_chuyen_nhanh

        self._dang_chon = False
        self._diem_bam = None
        self._dang_keo = False
        self._drag_proxy = None
        self._nen_hien_tai = theme.MAU_THE

        self._dung_giao_dien()
        self.cap_nhat(cong_viec)
        self._gan_su_kien(self)

        self.bind("<Configure>", self._khi_doi_kich_thuoc, add="+")

    # ---------------------------------------------------------------- dựng giao diện
    def _dung_giao_dien(self):
        self.noi_dung = tk.Frame(self, bg=theme.MAU_THE)
        self.noi_dung.pack(fill="both", expand=True, padx=13, pady=11)

        # Hàng 1: Pill Mã + Nhãn (trái) | Badge mức ưu tiên (phải)
        self.hang_tren = tk.Frame(self.noi_dung, bg=theme.MAU_THE)
        self.hang_tren.pack(fill="x")

        self.lbl_ma = ctk.CTkLabel(
            self.hang_tren, text="", font=theme.FONT_NHO_DAM,
            corner_radius=0, height=22, padx=7,
            fg_color="#eef2f6", text_color="#334155", bg_color=theme.MAU_THE
        )
        self.lbl_ma.pack(side="left", padx=(0, 6))

        self.lbl_nhan = ctk.CTkLabel(
            self.hang_tren, text="", font=theme.FONT_NHO_DAM,
            corner_radius=0, height=22, padx=8, bg_color=theme.MAU_THE
        )
        self.lbl_nhan.pack(side="left")

        self.lbl_uu_tien = ctk.CTkLabel(
            self.hang_tren, text="", font=theme.FONT_NHO_DAM,
            corner_radius=0, height=22, padx=9, bg_color=theme.MAU_THE
        )
        self.lbl_uu_tien.pack(side="right")

        # Hàng 2: Tiêu đề & tóm tắt mô tả
        self.lbl_tieu_de = tk.Label(
            self.noi_dung, bg=theme.MAU_THE, fg="#0f172a",
            font=theme.FONT_DAM, anchor="w", justify="left", wraplength=210
        )
        self.lbl_tieu_de.pack(fill="x", pady=(7, 2))

        self.lbl_mo_ta = tk.Label(
            self.noi_dung, bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU,
            font=theme.FONT_NHO, anchor="w", justify="left", wraplength=210
        )

        # Thanh 4 đoạn tiến độ công đoạn quy trình
        self.khung_buoc = tk.Frame(self.noi_dung, bg=theme.MAU_THE)
        self.khung_buoc.pack(fill="x", pady=(6, 0))
        self.cac_buoc = []
        for i in range(4):
            self.khung_buoc.columnconfigure(i, weight=1, uniform="buoc")
            pad_r = (0, 4) if i < 3 else (0, 0)
            seg = ctk.CTkFrame(
                self.khung_buoc, width=10, height=4, corner_radius=0,
                fg_color="#e2e8f0", bg_color=theme.MAU_THE
            )
            seg.grid(row=0, column=i, sticky="ew", padx=pad_r)
            self.cac_buoc.append(seg)

        # Đường kẻ phân cách
        self.duong_ke = tk.Frame(self.noi_dung, bg=theme.MAU_VIEN, height=1)
        self.duong_ke.pack(fill="x", pady=(7, 7))

        # Hàng 3: Người phụ trách (avatar đa sắc chữ trắng) + pill bình luận
        self.hang_phu = tk.Frame(self.noi_dung, bg=theme.MAU_THE)
        self.hang_phu.pack(fill="x")

        self.lbl_avatar = ctk.CTkLabel(
            self.hang_phu, text="?", width=24, height=24, corner_radius=0,
            fg_color=theme.MAU_CHINH, text_color="white",
            font=theme.FONT_NHO_DAM, bg_color=theme.MAU_THE
        )
        self.lbl_avatar.pack(side="left", padx=(0, 7))

        self.lbl_nguoi = tk.Label(
            self.hang_phu, bg=theme.MAU_THE, fg="#1e293b",
            font=theme.FONT_NHO_DAM, anchor="w"
        )
        self.lbl_nguoi.pack(side="left", fill="x", expand=True)

        self.lbl_binh_luan = ctk.CTkLabel(
            self.hang_phu, text="", corner_radius=0, height=22, padx=7,
            fg_color="#eef2f6", text_color="#334155",
            font=theme.FONT_NHO_DAM, bg_color=theme.MAU_THE
        )

        self.btn_chuyen_tiep = ctk.CTkButton(
            self.hang_phu, text="Tiếp >", command=self._xu_ly_chuyen_nhanh,
            width=54, height=22, corner_radius=0,
            fg_color="#eef2f6", hover_color=theme.MAU_CHINH_NHAT,
            border_width=0, text_color=theme.MAU_CHINH_DAM,
            font=theme.FONT_NHO_DAM, bg_color=theme.MAU_THE
        )

        # Hàng 4: Dải trạng thái hạn chót & cảnh báo đa hình có màu ngữ nghĩa
        self.khung_han = ctk.CTkFrame(
            self.noi_dung, corner_radius=0, border_width=1, bg_color=theme.MAU_THE
        )
        self.khung_han.pack(fill="x", pady=(7, 0))

        self.lbl_han = tk.Label(
            self.khung_han, font=theme.FONT_NHO,
            anchor="w", justify="left", wraplength=190
        )
        self.lbl_han.pack(fill="x", padx=9, pady=5)

    # ---------------------------------------------------------------- hiển thị dữ liệu
    def cap_nhat(self, cong_viec):
        """Đổ dữ liệu của công việc lên thẻ."""
        cv = cong_viec
        self.cong_viec = cv

        nen_ut = theme.MAU_NEN_BADGE_UU_TIEN.get(cv.muc_uu_tien, theme.MAU_NEN)
        chu_ut = theme.MAU_CHU_BADGE_UU_TIEN.get(cv.muc_uu_tien, theme.MAU_CHU)

        ten_nhan = cv.nhan or "Không nhãn"
        nen_nhan = theme.MAU_NEN_NHAN_TAG.get(ten_nhan, theme.MAU_NEN)
        chu_nhan = theme.MAU_NHAN_TAG.get(ten_nhan, theme.MAU_CHU_NHAN)

        self.lbl_ma.configure(text=cv.ma_cong_viec)
        self.lbl_nhan.configure(text=ten_nhan, fg_color=nen_nhan, text_color=chu_nhan)

        self.lbl_uu_tien.configure(
            text=cv.muc_uu_tien, fg_color=nen_ut, text_color=chu_ut
        )

        self.lbl_tieu_de.configure(text=cv.tieu_de)

        mo_ta = (cv.mo_ta or "").strip().replace("\n", " ")
        if mo_ta:
            if len(mo_ta) > 78:
                mo_ta = mo_ta[:75].rstrip() + "..."
            self.lbl_mo_ta.configure(text=mo_ta)
            self.lbl_mo_ta.pack(fill="x", pady=(0, 2), before=self.khung_buoc)
        else:
            self.lbl_mo_ta.pack_forget()

        try:
            muc_buoc = TRANG_THAI_HOP_LE.index(cv.trang_thai) + 1
        except ValueError:
            muc_buoc = 1
        mau_buoc = theme.MAU_TRANG_THAI_COT.get(cv.trang_thai, theme.MAU_CHINH)
        for idx, seg in enumerate(self.cac_buoc):
            seg.configure(fg_color=mau_buoc if idx < muc_buoc else "#e2e8f0")

        ten_hien_thi = self.ten_nguoi_map.get(cv.nguoi_phu_trach, cv.nguoi_phu_trach)
        self.lbl_avatar.configure(
            text=tao_chu_viet_tat(ten_hien_thi),
            fg_color=theme.mau_avatar(cv.nguoi_phu_trach)
        )
        self.lbl_nguoi.configure(text=ten_hien_thi)

        so_bl = len(getattr(cv, "danh_sach_binh_luan", []))
        if so_bl > 0:
            self.lbl_binh_luan.configure(text=f"{so_bl} bình luận")
            self.lbl_binh_luan.pack(side="right")
        else:
            self.lbl_binh_luan.pack_forget()

        if self.khi_chuyen_nhanh and not cv.is_hoan_thanh():
            self.btn_chuyen_tiep.pack(side="right", padx=(4, 0))
        else:
            self.btn_chuyen_tiep.pack_forget()

        if cv.is_hoan_thanh():
            if getattr(cv, "hoan_thanh_tre", False):
                nen_han, chu_han, vien_han = "#fef3c7", "#b45309", "#fde68a"
                noi_dung_han = f"[Trễ hạn] Hoàn thành ({cv.ngay_ket_thuc})"
            else:
                nen_han, chu_han, vien_han = "#dcfce7", "#166534", "#bbf7d0"
                noi_dung_han = f"Hoàn thành ({cv.ngay_ket_thuc})"
        else:
            if cv.da_qua_han():
                nen_han, chu_han, vien_han = "#fee2e2", "#b91c1c", "#fecaca"
            elif cv.muc_uu_tien == "Khẩn":
                nen_han, chu_han, vien_han = "#ffe4e6", "#9f1239", "#fecdd3"
            else:
                nen_han, chu_han, vien_han = "#f1f5f9", "#475569", "#e2e8f0"
            noi_dung_han = f"Hạn: {cv.ngay_ket_thuc}  •  {cv.canh_bao()}"

        self.khung_han.configure(fg_color=nen_han, border_color=vien_han)
        self.lbl_han.configure(text=noi_dung_han, bg=nen_han, fg=chu_han)

        self.dat_chon(self._dang_chon)

    def _vien_mac_dinh(self):
        if getattr(self.cong_viec, "muc_uu_tien", "") == "Khẩn":
            return "#fda4af"
        return theme.MAU_VIEN_THE

    def dat_chon(self, duoc_chon: bool):
        """Tô viền đậm màu Lavender khi thẻ đang được chọn."""
        self._dang_chon = duoc_chon
        if duoc_chon:
            self.configure(border_color=theme.MAU_CHINH, border_width=2)
        else:
            self.configure(border_color=self._vien_mac_dinh(), border_width=1)

    def chon(self, duoc_chon: bool):
        """Đặt trạng thái chọn cho thẻ (alias tương thích ngược)."""
        self.dat_chon(duoc_chon)

    # ---------------------------------------------------------------- sự kiện
    def _gan_su_kien(self, widget):
        """Gắn sự kiện cho thẻ và toàn bộ widget con để tương tác mượt."""
        try:
            widget.bind("<Button-1>", self._xu_ly_click, add="+")
            widget.bind("<Double-Button-1>", self._xu_ly_double_click, add="+")
            widget.bind("<Button-3>", self._xu_ly_chuot_phai, add="+")
            widget.bind("<Button-2>", self._xu_ly_chuot_phai, add="+")
            widget.bind("<B1-Motion>", self._xu_ly_keo, add="+")
            widget.bind("<ButtonRelease-1>", self._xu_ly_tha, add="+")
            widget.bind("<Enter>", self._khi_re_vao, add="+")
            widget.bind("<Leave>", self._khi_re_ra, add="+")
            widget.bind("<MouseWheel>", self._xu_ly_cuon, add="+")
            widget.bind("<Button-4>", self._xu_ly_cuon, add="+")
            widget.bind("<Button-5>", self._xu_ly_cuon, add="+")
        except (tk.TclError, ValueError, NotImplementedError) as loi:
            # Widget đã bị hủy, hoặc loại widget (CustomTkinter) không cho gắn thêm sự kiện
            logger.debug(f"Bỏ qua gắn sự kiện cho {type(widget).__name__}: {loi}")
        for con in widget.winfo_children():
            self._gan_su_kien(con)

    def _xu_ly_cuon(self, event):
        """Chuyển tiếp sự kiện cuộn chuột lên cột CotKanban cha."""
        w = self.master
        while w and not hasattr(w, "cuon"):
            w = getattr(w, "master", None)
        if w and hasattr(w, "cuon"):
            w.cuon(event)

    def _xu_ly_click(self, event):
        self._diem_bam = (event.x_root, event.y_root)
        self._dang_keo = False
        if self.khi_chon:
            try:
                self.khi_chon(self.cong_viec, self)
            except TypeError:
                self.khi_chon(self.cong_viec)

    def _xu_ly_keo(self, event):
        if self._diem_bam is None:
            return
        if not self._dang_keo:
            dx = event.x_root - self._diem_bam[0]
            dy = event.y_root - self._diem_bam[1]
            if dx * dx + dy * dy < 25:
                return
            self._dang_keo = True
            self._tao_drag_proxy(event)
        else:
            self._cap_nhat_drag_proxy(event)
        if self.khi_keo:
            self.khi_keo(self.cong_viec, event)

    def _xu_ly_tha(self, event):
        if self._dang_keo:
            self._dang_keo = False
            self._xoa_drag_proxy()
            if self.khi_tha:
                self.khi_tha(self.cong_viec, event)
        self._diem_bam = None

    def _tao_drag_proxy(self, event):
        """Tạo thẻ nổi bán trong suốt hiển thị thông tin thẻ di chuyển theo chuột."""
        self._xoa_drag_proxy()
        try:
            self.configure(fg_color="#f1f5f9", border_color=theme.MAU_CHINH)
            proxy = tk.Toplevel(self)
            proxy.overrideredirect(True)
            proxy.attributes("-topmost", True)
            try:
                proxy.attributes("-alpha", 0.92)
            except Exception:
                pass
            khung = tk.Frame(
                proxy, bg="#ffffff",
                highlightthickness=2, highlightbackground=theme.MAU_CHINH,
                padx=10, pady=7
            )
            khung.pack(fill="both", expand=True)

            hang1 = tk.Frame(khung, bg="#ffffff")
            hang1.pack(fill="x")
            lbl_ma = tk.Label(
                hang1, text=f"❖ {self.cong_viec.ma_cong_viec}",
                bg="#e9e8f4", fg="#6d669b",
                font=theme.FONT_NHO_DAM, padx=6, pady=2
            )
            lbl_ma.pack(side="left")

            lbl_ut = tk.Label(
                hang1, text=self.cong_viec.muc_uu_tien,
                bg=theme.MAU_NEN_BADGE_UU_TIEN.get(self.cong_viec.muc_uu_tien, "#f1f5f9"),
                fg=theme.MAU_CHU_BADGE_UU_TIEN.get(self.cong_viec.muc_uu_tien, "#1e1b33"),
                font=theme.FONT_NHO_DAM, padx=6, pady=2
            )
            lbl_ut.pack(side="right", padx=(8, 0))

            tieu_de = self.cong_viec.tieu_de
            if len(tieu_de) > 30:
                tieu_de = tieu_de[:28].rstrip() + "..."
            lbl_td = tk.Label(
                khung, text=tieu_de, bg="#ffffff", fg="#0f172a",
                font=theme.FONT_DAM, anchor="w"
            )
            lbl_td.pack(fill="x", pady=(4, 0))

            proxy.geometry(f"+{event.x_root + 15}+{event.y_root + 15}")
            self._drag_proxy = proxy
        except Exception:
            self._drag_proxy = None

    def _cap_nhat_drag_proxy(self, event):
        if getattr(self, "_drag_proxy", None):
            try:
                if self._drag_proxy.winfo_exists():
                    self._drag_proxy.geometry(f"+{event.x_root + 15}+{event.y_root + 15}")
            except Exception:
                pass

    def _xoa_drag_proxy(self):
        proxy = getattr(self, "_drag_proxy", None)
        if proxy:
            try:
                if proxy.winfo_exists():
                    proxy.destroy()
            except Exception:
                pass
            self._drag_proxy = None
        try:
            self.configure(fg_color=self._nen_hien_tai, border_color=self._vien_mac_dinh())
        except Exception:
            pass

    def _xu_ly_double_click(self, event):
        if self.khi_mo:
            self.khi_mo(self.cong_viec)

    def _xu_ly_chuot_phai(self, event):
        if self.khi_menu:
            self.khi_menu(self.cong_viec, event)

    def _khi_re_vao(self, event):
        self._to_nen(theme.MAU_THE_HOVER)
        if not self._dang_chon:
            self.configure(border_color=theme.MAU_VIEN_HOVER)

    def _khi_re_ra(self, event):
        try:
            x, y = self.winfo_rootx(), self.winfo_rooty()
            if (x <= event.x_root < x + self.winfo_width()
                    and y <= event.y_root < y + self.winfo_height()):
                return
        except tk.TclError:
            return
        self._to_nen(theme.MAU_THE)
        if not self._dang_chon:
            self.configure(border_color=self._vien_mac_dinh())

    def _to_nen(self, mau):
        """Đổi màu nền thẻ và đồng bộ bg_color các badge khi hover."""
        if self._nen_hien_tai == mau:
            return
        self._nen_hien_tai = mau
        self.configure(fg_color=mau)
        for w in (self.noi_dung, self.hang_tren, self.lbl_tieu_de,
                  self.lbl_mo_ta, self.khung_buoc, self.hang_phu, self.lbl_nguoi):
            w.configure(bg=mau)
        for badge in (self.lbl_ma, self.lbl_nhan, self.lbl_uu_tien,
                      self.lbl_avatar, self.lbl_binh_luan, self.btn_chuyen_tiep,
                      self.khung_han, *self.cac_buoc):
            badge.configure(bg_color=mau)

    def _xu_ly_chuyen_nhanh(self):
        if self.khi_chuyen_nhanh and self.cong_viec:
            self.khi_chuyen_nhanh(self.cong_viec)

    def _khi_doi_kich_thuoc(self, event):
        wrap = max(event.width - 30, 120)
        self.lbl_tieu_de.configure(wraplength=wrap)
        self.lbl_mo_ta.configure(wraplength=wrap)
        self.lbl_han.configure(wraplength=max(event.width - 48, 110))
