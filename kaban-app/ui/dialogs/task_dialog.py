"""TaskDialog: Hộp thoại thêm / sửa / xem chi tiết công việc và trao đổi bình luận."""
import re
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk, messagebox
import customtkinter as ctk

from config import NHAN_HOP_LE, MUC_UU_TIEN_HOP_LE
from exceptions import (
    KanbanException, DuLieuKhongHopLeError, KhongCoQuyenError,
    KhongTimThayError, LoiLuuTruError, XungDotDuLieuError
)
from ui.styles import theme
from utils.helpers import can_giua


class TaskDialog(tk.Toplevel):
    """Hộp thoại tạo mới hoặc chỉnh sửa/xem chi tiết Task kèm validate và bắt ngoại lệ."""

    def __init__(self, master, ql, du_an, cong_viec=None, khi_xong=None, trang_thai_mac_dinh=None):
        super().__init__(master)
        self.ql = ql
        self.du_an = du_an
        self.cong_viec = cong_viec
        self.khi_xong = khi_xong
        self._da_thay_doi_bl = False

        if cong_viec is not None:
            self.co_quyen_sua = self.ql.kiem_tra_quyen_cong_viec(cong_viec)
        else:
            self.co_quyen_sua = self.ql.kiem_tra_quyen_du_an(du_an)

        tieu_de_cs = f"Chi tiết công việc - {cong_viec.ma_cong_viec}" if cong_viec else "Thêm công việc mới"
        self.title(tieu_de_cs)
        self.configure(bg=theme.MAU_THE)
        self.minsize(640, 580)
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self._dong)

        hom_nay = date.today()
        ds_tv = list(du_an.thanh_vien_tham_gia)
        tt_dau = trang_thai_mac_dinh if trang_thai_mac_dinh in du_an.danh_sach_cot else du_an.danh_sach_cot[0]

        self.var_nguoi = tk.StringVar(value=ds_tv[0] if ds_tv else "")
        self.var_nhan = tk.StringVar(value=NHAN_HOP_LE[0])
        self.var_uu_tien = tk.StringVar(value="Trung bình")
        self.var_trang_thai = tk.StringVar(value=tt_dau)
        self.var_khan_cap = tk.BooleanVar(value=False)

        self._ma_moi = cong_viec.ma_cong_viec if cong_viec else self._sinh_ma()
        self._ngay_bd_mac_dinh = hom_nay.isoformat()
        self._ngay_kt_mac_dinh = (hom_nay + timedelta(days=7)).isoformat()

        self._dung_giao_dien()
        if cong_viec:
            self._do_du_lieu_cu()
        else:
            theme.dat_gia_tri_entry(self.ent_ma, self._ma_moi)
            theme.dat_gia_tri_entry(self.ent_bat_dau, self._ngay_bd_mac_dinh)
            theme.dat_gia_tri_entry(self.ent_ket_thuc, self._ngay_kt_mac_dinh)
            self._cap_nhat_goi_y_han()

        can_giua(self, 740, 780 if cong_viec else 620)
        if self.co_quyen_sua:
            self.ent_tieu_de.focus_set()
        self.bind("<Escape>", lambda _e: self._dong())
        self.bind("<Control-Return>", lambda _e: self.luu())
        self.wait_visibility()
        self.grab_set()

    def _nhan(self, cha, text):
        lbl = tk.Label(cha, text=text, bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w")
        lbl.pack(fill="x", pady=(0, 2))
        return lbl

    def _dung_giao_dien(self):
        khung_ngoai = tk.Frame(self, bg=theme.MAU_THE)
        khung_ngoai.pack(fill="both", expand=True)

        tieu_de_hd = "Thông tin công việc" if not self.cong_viec else (
            f"Chi tiết công việc {self.cong_viec.ma_cong_viec} (Chỉ xem)" if not self.co_quyen_sua
            else f"Cập nhật công việc {self.cong_viec.ma_cong_viec}"
        )
        theme.tao_header_figma(khung_ngoai, tieu_de=tieu_de_hd, badge_text="CV", cao=74,
                               subtitle=f"Dự án {self.du_an.ma_du_an} — {self.du_an.ten_du_an}")

        footer = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=24, pady=10)
        footer.pack(side="bottom", fill="x")
        tk.Frame(footer, bg="#edf1f4", height=1).pack(fill="x", pady=(0, 10))

        hang_nut = tk.Frame(footer, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")

        self.btn_luu = theme.tao_nut_chinh(hang_nut, text="Lưu công việc", command=self.luu, width=144, height=38)
        self.btn_luu.pack(side="right")
        theme.tao_nut_phu(hang_nut, text="Đóng" if not self.co_quyen_sua else "Hủy", command=self._dong, width=96, height=38).pack(side="right", padx=(0, 8))

        if self.cong_viec and self.ql.nguoi_dung_hien_tai.co_quyen_xoa_cong_viec():
            theme.tao_nut_nguy_hiem(hang_nut, text="Xóa công việc", command=self._xoa_cong_viec, width=126, height=38).pack(side="left", padx=(0, 10))

        noi_dung_tb = "Chế độ chỉ xem: chỉ người phụ trách hoặc Quản trị viên mới sửa được." if (self.cong_viec and not self.co_quyen_sua) else ""
        self.lbl_thong_bao = tk.Label(hang_nut, text=noi_dung_tb, bg=theme.MAU_THE, fg=theme.MAU_CANH_BAO if noi_dung_tb else theme.MAU_LOI, font=theme.FONT_NHO, anchor="w", wraplength=380)
        self.lbl_thong_bao.pack(side="left", fill="x", expand=True)

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=24, pady=10)
        khung.pack(fill="both", expand=True)

        if self.cong_viec:
            cv = self.cong_viec
            mau_canh = theme.MAU_HOAN_THANH if cv.is_hoan_thanh() else (theme.MAU_LOI if cv.da_qua_han() else theme.MAU_CHINH_DAM)
            nen_banner = theme.MAU_NEN_LOI_NHAT if (not cv.is_hoan_thanh() and cv.da_qua_han()) else theme.MAU_CHINH_NHAT
            banner = ctk.CTkFrame(khung, fg_color=nen_banner, corner_radius=0, border_width=0)
            banner.pack(fill="x", pady=(0, 8))
            tk.Label(banner, text=f"{cv.lay_loai_cong_viec()}  •  Cột: {cv.trang_thai}  •  {cv.canh_bao()}", bg=nen_banner, fg=mau_canh, font=theme.FONT_NHO_DAM, anchor="w", padx=12, pady=5).pack(fill="x")

        # Hàng 1: Mã & Tiêu đề
        hang1 = tk.Frame(khung, bg=theme.MAU_THE)
        hang1.pack(fill="x", pady=(0, 7))
        hang1.columnconfigure(0, weight=1)
        hang1.columnconfigure(1, weight=2)

        c1 = tk.Frame(hang1, bg=theme.MAU_THE)
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._nhan(c1, "Mã công việc")
        self.ent_ma = theme.tao_entry(c1, cao=34, state="disabled")
        self.ent_ma.pack(fill="x")

        c2 = tk.Frame(hang1, bg=theme.MAU_THE)
        c2.grid(row=0, column=1, sticky="ew")
        self._nhan(c2, "Tiêu đề công việc *")
        self.ent_tieu_de = theme.tao_entry(c2, placeholder="Nhập tiêu đề công việc", cao=34)
        self.ent_tieu_de.pack(fill="x")

        # Hàng 2: Mô tả
        vung_mota = tk.Frame(khung, bg=theme.MAU_THE)
        vung_mota.pack(fill="x", pady=(0, 7))
        self._nhan(vung_mota, "Mô tả chi tiết")
        self.txt_mo_ta = ctk.CTkTextbox(vung_mota, height=48, corner_radius=0, fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1, text_color=theme.MAU_CHU, font=theme.FONT_CHUAN, wrap="word")
        self.txt_mo_ta.pack(fill="x")

        # Hàng 3: Trạng thái, Ưu tiên, Nhãn
        hang3 = tk.Frame(khung, bg=theme.MAU_THE)
        hang3.pack(fill="x", pady=(0, 7))
        for i in range(3):
            hang3.columnconfigure(i, weight=1, uniform="h3")

        f_tt = tk.Frame(hang3, bg=theme.MAU_THE)
        f_tt.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._nhan(f_tt, "Trạng thái")
        self.cbb_trang_thai = theme.tao_combobox(f_tt, values=self.du_an.danh_sach_cot, variable=self.var_trang_thai, height=34)
        self.cbb_trang_thai.pack(fill="x")

        f_ut = tk.Frame(hang3, bg=theme.MAU_THE)
        f_ut.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self._nhan(f_ut, "Mức ưu tiên")
        self.cbb_uu_tien = theme.tao_combobox(f_ut, values=MUC_UU_TIEN_HOP_LE, variable=self.var_uu_tien, command=self._khi_chon_uu_tien, height=34)
        self.cbb_uu_tien.pack(fill="x")

        f_nh = tk.Frame(hang3, bg=theme.MAU_THE)
        f_nh.grid(row=0, column=2, sticky="ew")
        self._nhan(f_nh, "Nhãn")
        self.cbb_nhan = theme.tao_combobox(f_nh, values=NHAN_HOP_LE, variable=self.var_nhan, height=34)
        self.cbb_nhan.pack(fill="x")

        # Hàng 4: Người phụ trách
        vung_nguoi = tk.Frame(khung, bg=theme.MAU_THE)
        vung_nguoi.pack(fill="x", pady=(0, 7))
        self._nhan(vung_nguoi, "Người phụ trách *")
        ds_tv = list(self.du_an.thanh_vien_tham_gia)
        self.cbb_nguoi = theme.tao_combobox(vung_nguoi, values=ds_tv, variable=self.var_nguoi, height=34)
        self.cbb_nguoi.pack(fill="x")

        # Hàng 5: Ngày bắt đầu & Ngày kết thúc
        hang5 = tk.Frame(khung, bg=theme.MAU_THE)
        hang5.pack(fill="x", pady=(0, 7))
        hang5.columnconfigure(0, weight=1, uniform="h5")
        hang5.columnconfigure(1, weight=1, uniform="h5")

        f_bd = tk.Frame(hang5, bg=theme.MAU_THE)
        f_bd.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._nhan(f_bd, "Ngày bắt đầu (YYYY-MM-DD)")
        self.ent_bat_dau = theme.tao_entry(f_bd, placeholder="YYYY-MM-DD", cao=34)
        self.ent_bat_dau.pack(fill="x")

        f_kt = tk.Frame(hang5, bg=theme.MAU_THE)
        f_kt.grid(row=0, column=1, sticky="ew")
        dau_kt = tk.Frame(f_kt, bg=theme.MAU_THE)
        dau_kt.pack(fill="x", pady=(0, 2))
        tk.Label(dau_kt, text="Ngày kết thúc *", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w").pack(side="left")
        if self.co_quyen_sua:
            for so_ngay in (14, 7, 3):
                ctk.CTkButton(dau_kt, text=f"+{so_ngay}d", command=lambda n=so_ngay: self._chon_nhanh_han(n), width=46, height=20, corner_radius=0, fg_color=theme.MAU_CHINH_NHAT, hover_color="#c6e6e0", border_width=0, text_color=theme.MAU_CHINH_DAM, bg_color=theme.MAU_THE, font=theme.FONT_NHO_DAM).pack(side="right", padx=(3, 0))

        self.ent_ket_thuc = theme.tao_entry(f_kt, placeholder="YYYY-MM-DD", cao=34)
        self.ent_ket_thuc.pack(fill="x")
        self.ent_ket_thuc.bind("<KeyRelease>", self._cap_nhat_goi_y_han)

        self.lbl_dem_ngay = tk.Label(f_kt, text="", bg=theme.MAU_THE, font=theme.FONT_NHO, anchor="w")
        self.lbl_dem_ngay.pack(fill="x", pady=(2, 0))

        # Checkbox Khẩn
        self.chk_khan = ctk.CTkCheckBox(khung, text="Là công việc khẩn cấp (CongViecKhan)", variable=self.var_khan_cap, command=self._khi_tick_khan_cap, font=theme.FONT_CHUAN, text_color=theme.MAU_CHU_NHAN, fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM, border_color=theme.MAU_VIEN_THE, corner_radius=0, checkbox_width=18, checkbox_height=18)
        self.chk_khan.pack(anchor="w", pady=(2, 6))

        if self.cong_viec:
            self._dung_binh_luan(khung)

    def _cap_nhat_goi_y_han(self, _event=None):
        val = self.ent_ket_thuc.get().strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", val):
            self.lbl_dem_ngay.configure(text="")
            return
        try:
            d_kt = datetime.strptime(val, "%Y-%m-%d").date()
            delta = (d_kt - date.today()).days
            if delta < 0:
                self.lbl_dem_ngay.configure(text=f"(Quá hạn {-delta} ngày)", fg=theme.MAU_LOI)
            elif delta == 0:
                self.lbl_dem_ngay.configure(text="(Hạn là hôm nay)", fg=theme.MAU_CANH_BAO)
            else:
                self.lbl_dem_ngay.configure(text=f"(Còn {delta} ngày)", fg=theme.MAU_HOAN_THANH)
        except ValueError:
            self.lbl_dem_ngay.configure(text="")

    def _chon_nhanh_han(self, so_ngay: int):
        ngay_moi = (date.today() + timedelta(days=so_ngay)).isoformat()
        theme.dat_gia_tri_entry(self.ent_ket_thuc, ngay_moi)
        self._cap_nhat_goi_y_han()

    def _khi_tick_khan_cap(self):
        if self.var_khan_cap.get():
            self.var_uu_tien.set("Khẩn")
        elif self.var_uu_tien.get() == "Khẩn":
            self.var_uu_tien.set("Trung bình")

    def _khi_chon_uu_tien(self, gia_tri):
        self.var_khan_cap.set(gia_tri == "Khẩn")

    def _do_du_lieu_cu(self):
        cv = self.cong_viec
        theme.dat_gia_tri_entry(self.ent_ma, cv.ma_cong_viec)
        theme.dat_gia_tri_entry(self.ent_tieu_de, cv.tieu_de)
        self.txt_mo_ta.insert("1.0", cv.mo_ta or "")
        self.var_nguoi.set(cv.nguoi_phu_trach)
        self.var_nhan.set(cv.nhan or NHAN_HOP_LE[0])
        self.var_uu_tien.set(cv.muc_uu_tien)
        self.var_trang_thai.set(cv.trang_thai)
        theme.dat_gia_tri_entry(self.ent_bat_dau, cv.ngay_bat_dau)
        theme.dat_gia_tri_entry(self.ent_ket_thuc, cv.ngay_ket_thuc)
        self._cap_nhat_goi_y_han()
        self.var_khan_cap.set(cv.muc_uu_tien == "Khẩn")

        self.cbb_trang_thai.configure(state="disabled")
        if cv.muc_uu_tien == "Khẩn":
            self.cbb_uu_tien.configure(state="disabled")
            self.chk_khan.configure(state="disabled")

        if not self.co_quyen_sua:
            for w in (self.ent_tieu_de, self.ent_bat_dau, self.ent_ket_thuc):
                w.configure(state="disabled", fg_color=theme.MAU_O_NHAP_KHOA, text_color=theme.MAU_CHU_PHU)
            self.txt_mo_ta.configure(state="disabled", fg_color=theme.MAU_O_NHAP_KHOA, text_color=theme.MAU_CHU_PHU)
            for cbb in (self.cbb_uu_tien, self.cbb_nhan, self.cbb_nguoi):
                cbb.configure(state="disabled")
            self.chk_khan.configure(state="disabled")
            self.btn_luu.configure(state="disabled", fg_color=theme.MAU_DISABLED_NEN)

    def _sinh_ma(self):
        so = [int(m.group(1)) for cv in self.du_an.cong_viec if (m := re.fullmatch(r"CV-(\d+)", str(cv.ma_cong_viec)))]
        return f"CV-{(max(so) + 1 if so else 1):03d}"

    def _kiem_tra_ngay(self, bat_dau, ket_thuc):
        for ten, gia_tri in (("Ngày bắt đầu", bat_dau), ("Ngày kết thúc", ket_thuc)):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", gia_tri):
                return f"{ten} phải có dạng YYYY-MM-DD (ví dụ 2026-10-25)."
            try:
                datetime.strptime(gia_tri, "%Y-%m-%d")
            except ValueError:
                return f"{ten} không tồn tại trong lịch."
        if ket_thuc < bat_dau:
            return "Ngày kết thúc không được trước ngày bắt đầu."
        return None

    def luu(self):
        tieu_de = self.ent_tieu_de.get().strip()
        nguoi = self.var_nguoi.get().strip()
        if not tieu_de:
            self._bao_loi("Tiêu đề công việc không được để trống.", popup=True)
            self.ent_tieu_de.focus_set()
            return
        if len(tieu_de) < 2 or len(tieu_de) > 150:
            self._bao_loi("Tiêu đề công việc phải có độ dài từ 2 đến 150 ký tự.", popup=True)
            self.ent_tieu_de.focus_set()
            return
        if not nguoi:
            self._bao_loi("Người phụ trách không được để trống.", popup=True)
            return
        if nguoi not in self.du_an.thanh_vien_tham_gia:
            self._bao_loi(f"Người phụ trách '{nguoi}' chưa tham gia dự án này.", popup=True)
            return

        bat_dau = self.ent_bat_dau.get().strip()
        ket_thuc = self.ent_ket_thuc.get().strip()
        loi_ngay = self._kiem_tra_ngay(bat_dau, ket_thuc)
        if loi_ngay:
            self._bao_loi(loi_ngay, popup=True)
            return

        mo_ta = self.txt_mo_ta.get("1.0", "end-1c").strip()
        if len(mo_ta) > 1000:
            self._bao_loi("Mô tả công việc không được vượt quá 1000 ký tự.", popup=True)
            return

        du_lieu = {
            "tieu_de": tieu_de, "mo_ta": mo_ta, "nguoi_phu_trach": nguoi,
            "nhan": self.var_nhan.get(), "ngay_bat_dau": bat_dau, "ngay_ket_thuc": ket_thuc,
        }
        try:
            if self.cong_viec:
                if self.cong_viec.muc_uu_tien != "Khẩn":
                    du_lieu["muc_uu_tien"] = self.var_uu_tien.get()
                self.ql.cap_nhat_cong_viec(self.du_an, self.cong_viec.ma_cong_viec, du_lieu)
            else:
                du_lieu["muc_uu_tien"] = self.var_uu_tien.get()
                du_lieu["trang_thai"] = self.var_trang_thai.get()
                du_lieu["ma_cong_viec"] = self._sinh_ma()
                self.ql.tao_cong_viec(self.du_an, du_lieu, la_cong_viec_khan=self.var_khan_cap.get())
        except (DuLieuKhongHopLeError, KhongCoQuyenError, XungDotDuLieuError, LoiLuuTruError, KanbanException) as loi:
            self._bao_loi(loi.thong_diep, popup=True)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}", popup=True)
            return

        self.destroy()
        if self.khi_xong:
            self.khi_xong()

    def _bao_loi(self, thong_diep: str, popup: bool = False):
        if hasattr(self, "lbl_thong_bao") and self.lbl_thong_bao.winfo_exists():
            self.lbl_thong_bao.configure(text=thong_diep, fg=theme.MAU_LOI)
        if popup:
            messagebox.showwarning("Cảnh báo", thong_diep, parent=self)

    def _xoa_cong_viec(self):
        if not self.cong_viec:
            return
        if not messagebox.askyesno("Xác nhận xóa", f"Bạn chắc chắn muốn xóa công việc '{self.cong_viec.ma_cong_viec}'?", parent=self):
            return
        try:
            self.ql.xoa_cong_viec(self.du_an, self.cong_viec.ma_cong_viec)
        except (KhongCoQuyenError, LoiLuuTruError, KanbanException) as loi:
            self._bao_loi(loi.thong_diep, popup=True)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}", popup=True)
            return
        self.destroy()
        if self.khi_xong:
            self.khi_xong()

    def _dong(self):
        self.destroy()
        if self._da_thay_doi_bl and self.khi_xong:
            self.khi_xong()

    def _dung_binh_luan(self, khung):
        kv = ctk.CTkFrame(khung, fg_color=theme.MAU_O_NHAP, corner_radius=0, border_width=1, border_color=theme.MAU_VIEN)
        kv.pack(fill="both", expand=True, pady=(2, 2))

        dau_bl = tk.Frame(kv, bg=theme.MAU_O_NHAP)
        dau_bl.pack(fill="x", padx=12, pady=(8, 4))
        self.lbl_dem_bl = tk.Label(dau_bl, text="Bình luận trao đổi", bg=theme.MAU_O_NHAP, fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM)
        self.lbl_dem_bl.pack(side="left")

        theme.tao_nut_nguy_hiem(dau_bl, text="Xóa bình luận chọn", command=self.xoa_binh_luan, width=160, height=28, corner_radius=0, font=theme.FONT_NHO).pack(side="right")

        khung_ds = tk.Frame(kv, bg=theme.MAU_O_NHAP)
        khung_ds.pack(fill="both", expand=True, padx=12)
        self.lst_bl = tk.Listbox(khung_ds, height=3, font=theme.FONT_NHO, activestyle="none", bg="white", fg=theme.MAU_CHU, bd=1, relief="solid", highlightthickness=0, selectbackground=theme.MAU_CHINH_NHAT, selectforeground=theme.MAU_CHINH_DAM)
        thanh = ttk.Scrollbar(khung_ds, orient="vertical", command=self.lst_bl.yview)
        self.lst_bl.configure(yscrollcommand=thanh.set)
        self.lst_bl.pack(side="left", fill="both", expand=True)
        thanh.pack(side="right", fill="y")

        hang_gui = tk.Frame(kv, bg=theme.MAU_O_NHAP)
        hang_gui.pack(fill="x", padx=12, pady=(5, 8))
        self.ent_bl = theme.tao_entry(hang_gui, placeholder="Nhập nội dung bình luận...", cao=32, fg_color="white")
        self.ent_bl.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ent_bl.bind("<Return>", lambda _e: self.gui_binh_luan())
        theme.tao_nut_chinh(hang_gui, text="Gửi", command=self.gui_binh_luan, width=76, height=32).pack(side="right")

        self._nap_binh_luan()

    def _nap_binh_luan(self):
        self.lst_bl.delete(0, "end")
        ds_bl = self.cong_viec.danh_sach_binh_luan
        self.lbl_dem_bl.configure(text=f"Bình luận trao đổi ({len(ds_bl)})")
        for bl in ds_bl:
            self.lst_bl.insert("end", f"[{bl.thoi_gian}] {bl.nguoi_gui}: {bl.noi_dung}")
        if ds_bl:
            self.lst_bl.see("end")

    def gui_binh_luan(self):
        noi_dung = self.ent_bl.get().strip()
        if not noi_dung:
            self._bao_loi("Nội dung bình luận không được để trống.", popup=True)
            self.ent_bl.focus_set()
            return
        if len(noi_dung) > 500:
            self._bao_loi("Bình luận không được vượt quá 500 ký tự.", popup=True)
            return
        try:
            self.ql.them_binh_luan_cong_viec(self.du_an, self.cong_viec.ma_cong_viec, noi_dung)
        except (KhongCoQuyenError, LoiLuuTruError, KanbanException) as loi:
            self._bao_loi(loi.thong_diep, popup=True)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}", popup=True)
            return
        self._da_thay_doi_bl = True
        theme.dat_gia_tri_entry(self.ent_bl, "")
        self._nap_binh_luan()

    def xoa_binh_luan(self):
        chon = self.lst_bl.curselection()
        if not chon:
            self._bao_loi("Hãy chọn một bình luận trong danh sách để xóa.", popup=True)
            return
        bl = self.cong_viec.danh_sach_binh_luan[chon[0]]
        if not messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa bình luận này?", parent=self):
            return
        try:
            self.ql.xoa_binh_luan_cong_viec(self.du_an, self.cong_viec.ma_cong_viec, bl.ma_binh_luan)
        except (KhongCoQuyenError, LoiLuuTruError, KanbanException) as loi:
            self._bao_loi(loi.thong_diep, popup=True)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}", popup=True)
            return
        self._da_thay_doi_bl = True
        self._nap_binh_luan()


CongViecDialog = TaskDialog
