"""CommentBoxComponent: Thành phần giao diện quản lý danh sách và gửi bình luận trao đổi."""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import queue

from ui.styles import theme
from exceptions import KhongCoQuyenError, LoiLuuTruError, KanbanException
from logger import logger
from services.chat_protocol import tao_phong

CHU_KY_DOC_TIN_MS = 300   # giao diện đọc tin realtime mỗi 300 ms


class CommentBoxComponent(ctk.CTkFrame):
    """
    Component hiển thị và quản lý bình luận của một công việc:
    - Danh sách bình luận có thanh cuộn
    - Ô nhập nội dung và nút gửi
    - Nút xóa bình luận đang chọn
    """

    def __init__(self, master, ql, du_an, cong_viec, khi_thay_doi=None, bao_loi_cb=None, **kwargs):
        super().__init__(
            master, fg_color=theme.MAU_O_NHAP, corner_radius=0,
            border_width=1, border_color=theme.MAU_VIEN, **kwargs
        )
        self.ql = ql
        self.du_an = du_an
        self.cong_viec = cong_viec
        self.khi_thay_doi = khi_thay_doi
        self.bao_loi_cb = bao_loi_cb
        self._da_thay_doi = False
        self._chat = getattr(ql, "chat", None)
        self._phong = None
        self._hang_doi_tin = None
        self._id_after = None

        self._dung_giao_dien()
        self._bat_dau_realtime()

    def _dung_giao_dien(self):
        dau_bl = tk.Frame(self, bg=theme.MAU_O_NHAP)
        dau_bl.pack(side="top", fill="x", padx=12, pady=(8, 4))

        self.lbl_dem_bl = tk.Label(
            dau_bl, text="Bình luận trao đổi",
            bg=theme.MAU_O_NHAP, fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM
        )
        self.lbl_dem_bl.pack(side="left")

        self.lbl_ket_noi = tk.Label(dau_bl, text="", bg=theme.MAU_O_NHAP, font=theme.FONT_NHO)
        self.lbl_ket_noi.pack(side="left", padx=(10, 0))

        theme.tao_nut_nguy_hiem(
            dau_bl, text="Xóa bình luận chọn", command=self.xoa_binh_luan,
            width=160, height=28, corner_radius=0, font=theme.FONT_NHO
        ).pack(side="right")

        # Hàng nhập và gửi bình luận ở đáy với chiều cao to, thoáng
        hang_gui = tk.Frame(self, bg=theme.MAU_O_NHAP)
        hang_gui.pack(side="bottom", fill="x", padx=12, pady=(8, 10))

        self.ent_bl = theme.tao_entry(
            hang_gui, placeholder="Nhập nội dung bình luận trao đổi...",
            cao=38, fg_color="white", font=theme.FONT_CHUAN
        )
        self.ent_bl.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ent_bl.bind("<Return>", lambda _e: self.gui_binh_luan())

        theme.tao_nut_chinh(
            hang_gui, text="Gửi", command=self.gui_binh_luan,
            width=88, height=38, font=theme.FONT_DAM
        ).pack(side="right")

        # Danh sách bình luận ở giữa
        khung_ds = tk.Frame(self, bg=theme.MAU_O_NHAP)
        khung_ds.pack(side="top", fill="both", expand=True, padx=12, pady=(0, 2))

        self.lst_bl = tk.Listbox(
            khung_ds, height=4, font=theme.FONT_NHO, activestyle="none",
            bg="white", fg=theme.MAU_CHU, bd=1, relief="solid", highlightthickness=0,
            selectbackground=theme.MAU_CHINH_NHAT, selectforeground=theme.MAU_CHINH_DAM
        )
        thanh = ttk.Scrollbar(khung_ds, orient="vertical", command=self.lst_bl.yview)
        self.lst_bl.configure(yscrollcommand=thanh.set)
        self.lst_bl.pack(side="left", fill="both", expand=True)
        thanh.pack(side="right", fill="y")

        self.nap_binh_luan()

    def nap_binh_luan(self):
        self.lst_bl.delete(0, "end")
        ds_bl = getattr(self.cong_viec, "danh_sach_binh_luan", [])
        self.lbl_dem_bl.configure(text=f"Bình luận trao đổi ({len(ds_bl)})")
        for bl in ds_bl:
            self.lst_bl.insert("end", f"[{bl.thoi_gian}] {bl.nguoi_gui}: {bl.noi_dung}")
        if ds_bl:
            self.lst_bl.see("end")

    def _bao_loi(self, msg):
        if self.bao_loi_cb:
            self.bao_loi_cb(msg)
        else:
            messagebox.showwarning("Thông báo", msg, parent=self)

    def gui_binh_luan(self):
        noi_dung = self.ent_bl.get().strip()
        if not noi_dung:
            self._bao_loi("Nội dung bình luận không được để trống.")
            self.ent_bl.focus_set()
            return
        if len(noi_dung) > 500:
            self._bao_loi("Bình luận không được vượt quá 500 ký tự.")
            return
        try:
            bl = self.ql.them_binh_luan_cong_viec(self.du_an, self.cong_viec.ma_cong_viec, noi_dung)
        except (KhongCoQuyenError, LoiLuuTruError, KanbanException) as loi:
            self._bao_loi(loi.thong_diep)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}")
            return
        self._da_thay_doi = True
        self._phat({"loai": "binh_luan", "binh_luan": bl.to_dict()})
        theme.dat_gia_tri_entry(self.ent_bl, "")
        self.nap_binh_luan()
        if self.khi_thay_doi:
            self.khi_thay_doi()

    def xoa_binh_luan(self):
        chon = self.lst_bl.curselection()
        if not chon:
            self._bao_loi("Hãy chọn một bình luận trong danh sách để xóa.")
            return
        ds_bl = getattr(self.cong_viec, "danh_sach_binh_luan", [])
        if chon[0] >= len(ds_bl):
            return
        bl = ds_bl[chon[0]]
        if not messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa bình luận này?", parent=self):
            return
        try:
            self.ql.xoa_binh_luan_cong_viec(self.du_an, self.cong_viec.ma_cong_viec, bl.ma_binh_luan)
        except (KhongCoQuyenError, LoiLuuTruError, KanbanException) as loi:
            self._bao_loi(loi.thong_diep)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}")
            return
        self._da_thay_doi = True
        self._phat({"loai": "xoa_binh_luan", "ma_binh_luan": bl.ma_binh_luan,
                    "nguoi": getattr(self.ql.nguoi_dung_hien_tai, "ten_dang_nhap", "")})
        self.nap_binh_luan()
        if self.khi_thay_doi:
            self.khi_thay_doi()

    # ==================== BÌNH LUẬN THỜI GIAN THỰC (WebSocket) ====================
    def _bat_dau_realtime(self):
        if self._chat is None:
            self.lbl_ket_noi.configure(text="○ Ngoại tuyến", fg=theme.MAU_CHU_PHU)
            return
        nguoi = getattr(self.ql.nguoi_dung_hien_tai, "ten_dang_nhap", "")
        try:
            self._phong = tao_phong(self.du_an.ma_du_an, self.cong_viec.ma_cong_viec)
        except ValueError as loi:
            logger.warning(f"Không mở được kênh bình luận realtime: {loi}")
            self._chat = None
            self.lbl_ket_noi.configure(text="○ Ngoại tuyến", fg=theme.MAU_CHU_PHU)
            return
        self._hang_doi_tin = self._chat.vao_phong(self._phong, nguoi)
        self._doc_tin()

    def _phat(self, tin):
        if self._chat is not None and self._phong:
            self._chat.gui(dict(tin, phong=self._phong))

    def _doc_tin(self):
        """Chạy trên luồng giao diện: lấy tin từ hàng đợi và cập nhật danh sách."""
        co_thay_doi = False
        try:
            while True:
                tin = self._hang_doi_tin.get_nowait()
                co_thay_doi |= self._ap_dung_tin(tin)
        except queue.Empty:
            pass
        if co_thay_doi:
            self._da_thay_doi = True
            self.nap_binh_luan()
            if self.khi_thay_doi:
                self.khi_thay_doi()
        if self._chat.da_ket_noi:
            self.lbl_ket_noi.configure(text="● Trực tuyến", fg=theme.MAU_HOAN_THANH)
        else:
            self.lbl_ket_noi.configure(text="○ Đang kết nối lại...", fg=theme.MAU_CANH_BAO)
        self._id_after = self.after(CHU_KY_DOC_TIN_MS, self._doc_tin)

    def _ap_dung_tin(self, tin) -> bool:
        ma_cv = self.cong_viec.ma_cong_viec
        try:
            if tin["loai"] == "binh_luan":
                return self.ql.ap_dung_binh_luan_tu_xa(self.du_an, ma_cv, tin["binh_luan"]) is not None
            if tin["loai"] == "xoa_binh_luan":
                return self.ql.ap_dung_xoa_binh_luan_tu_xa(self.du_an, ma_cv, tin["ma_binh_luan"])
            if tin["loai"] == "lich_su":
                ket_qua = [self.ql.ap_dung_binh_luan_tu_xa(self.du_an, ma_cv, bl) for bl in tin["danh_sach"]]
                return any(kq is not None for kq in ket_qua)
        except KanbanException as loi:
            logger.error(f"Không áp dụng được bình luận realtime: {loi.thong_diep}")
        return False

    def destroy(self):
        if self._id_after is not None:
            try:
                self.after_cancel(self._id_after)
            except tk.TclError:
                pass
            self._id_after = None
        if self._chat is not None and self._hang_doi_tin is not None:
            self._chat.roi_phong(self._phong, self._hang_doi_tin)
            self._hang_doi_tin = None
        super().destroy()

    @property
    def da_thay_doi(self):
        return self._da_thay_doi
