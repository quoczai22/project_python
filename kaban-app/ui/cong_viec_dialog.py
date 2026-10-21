"""Hộp thoại thêm / sửa công việc theo thiết kế Figma (Design Kanban Modals)."""
import re
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk, messagebox
import customtkinter as ctk

from config import NHAN_HOP_LE, MUC_UU_TIEN_HOP_LE
from exceptions import KanbanException
from ui import theme
from ui.tien_ich import can_giua


class CongViecDialog(tk.Toplevel):
    """cong_viec=None -> thêm mới; có giá trị -> sửa. Lưu xong gọi khi_xong()."""

    def __init__(self, master, ql, du_an, cong_viec=None, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.du_an = du_an
        self.cong_viec = cong_viec
        self.khi_xong = khi_xong

        self.title("Sửa công việc" if cong_viec else "Thêm công việc mới")
        self.configure(bg=theme.MAU_NEN)
        self.resizable(False, False)
        self.transient(master)

        hom_nay = date.today()
        ds_tv = list(du_an.thanh_vien_tham_gia)
        self.var_ma = tk.StringVar(value=cong_viec.ma_cong_viec if cong_viec else self._sinh_ma())
        self.var_tieu_de = tk.StringVar()
        self.var_nguoi = tk.StringVar(value=ds_tv[0] if ds_tv else "")
        self.var_nhan = tk.StringVar(value=NHAN_HOP_LE[0])
        self.var_uu_tien = tk.StringVar(value="Trung bình")
        self.var_trang_thai = tk.StringVar(value=du_an.danh_sach_cot[0])
        self.var_bat_dau = tk.StringVar(value=hom_nay.isoformat())
        self.var_ket_thuc = tk.StringVar(value=(hom_nay + timedelta(days=7)).isoformat())
        self.var_khan_cap = tk.BooleanVar(value=False)

        self._dung_giao_dien()
        if cong_viec:
            self._do_du_lieu_cu()
        can_giua(self, 590, 740 if cong_viec else 590)
        self.ent_tieu_de.focus_set()
        self.bind("<Escape>", lambda e: self.destroy())
        self.wait_visibility()
        self.grab_set()

    # ------------------------------------------------------------ giao diện
    def _nhan(self, cha, text):
        lbl = tk.Label(cha, text=text, bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
                       font=theme.FONT_DAM, anchor="w")
        lbl.pack(fill="x", pady=(0, 4))
        return lbl

    def _dung_giao_dien(self):
        khung_ngoai = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=14,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_ngoai.pack(fill="both", expand=True, padx=12, pady=12)

        # Header chuẩn Figma: KANBAN / CÔNG VIỆC - THÔNG TIN CÔNG VIỆC + badge CV
        theme.tao_header_figma(
            khung_ngoai,
            eyebrow="KANBAN / CÔNG VIỆC",
            tieu_de="THÔNG TIN CÔNG VIỆC",
            badge_text="CV",
            cao=76
        )

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=26, pady=16)
        khung.pack(fill="both", expand=True)

        # Hàng 1 (2 cột): Mã công việc & Tiêu đề công việc
        hang1 = tk.Frame(khung, bg=theme.MAU_THE)
        hang1.pack(fill="x", pady=(0, 10))
        hang1.columnconfigure(0, weight=1)
        hang1.columnconfigure(1, weight=2)

        c1 = tk.Frame(hang1, bg=theme.MAU_THE)
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._nhan(c1, "Mã công việc (VD: CV-001)")
        self.ent_ma = ctk.CTkEntry(
            c1, textvariable=self.var_ma, height=36, corner_radius=6,
            fg_color="#f1f5f9", border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU_PHU, font=theme.FONT_DAM, state="disabled"
        )
        self.ent_ma.pack(fill="x")

        c2 = tk.Frame(hang1, bg=theme.MAU_THE)
        c2.grid(row=0, column=1, sticky="ew")
        self._nhan(c2, "Tiêu đề công việc *")
        self.ent_tieu_de = ctk.CTkEntry(
            c2, textvariable=self.var_tieu_de, placeholder_text="Nhập tiêu đề công việc",
            height=36, corner_radius=6, fg_color=theme.MAU_O_NHAP,
            border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.ent_tieu_de.pack(fill="x")

        # Hàng 2: Mô tả chi tiết
        vung_mota = tk.Frame(khung, bg=theme.MAU_THE)
        vung_mota.pack(fill="x", pady=(0, 10))
        self._nhan(vung_mota, "Mô tả chi tiết")
        self.txt_mo_ta = ctk.CTkTextbox(
            vung_mota, height=64, corner_radius=6, fg_color=theme.MAU_O_NHAP,
            border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN, wrap="word"
        )
        self.txt_mo_ta.pack(fill="x")

        # Hàng 3 (3 cột): Trạng thái, Mức ưu tiên, Nhãn
        hang3 = tk.Frame(khung, bg=theme.MAU_THE)
        hang3.pack(fill="x", pady=(0, 10))
        for i in range(3):
            hang3.columnconfigure(i, weight=1, uniform="h3")

        f_tt = tk.Frame(hang3, bg=theme.MAU_THE)
        f_tt.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._nhan(f_tt, "Trạng thái")
        self.cbb_trang_thai = ctk.CTkComboBox(
            f_tt, variable=self.var_trang_thai, values=list(self.du_an.danh_sach_cot),
            state="readonly", height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.cbb_trang_thai.pack(fill="x")

        f_ut = tk.Frame(hang3, bg=theme.MAU_THE)
        f_ut.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self._nhan(f_ut, "Mức ưu tiên")
        self.cbb_uu_tien = ctk.CTkComboBox(
            f_ut, variable=self.var_uu_tien, values=list(MUC_UU_TIEN_HOP_LE),
            command=self._khi_chon_uu_tien,
            state="readonly", height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.cbb_uu_tien.pack(fill="x")

        f_nh = tk.Frame(hang3, bg=theme.MAU_THE)
        f_nh.grid(row=0, column=2, sticky="ew")
        self._nhan(f_nh, "Nhãn")
        self.cbb_nhan = ctk.CTkComboBox(
            f_nh, variable=self.var_nhan, values=list(NHAN_HOP_LE),
            state="readonly", height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.cbb_nhan.pack(fill="x")

        # Hàng 4: Người được giao
        vung_nguoi = tk.Frame(khung, bg=theme.MAU_THE)
        vung_nguoi.pack(fill="x", pady=(0, 10))
        self._nhan(vung_nguoi, "Người được giao *")
        self.cbb_nguoi = ctk.CTkComboBox(
            vung_nguoi, variable=self.var_nguoi, values=list(self.du_an.thanh_vien_tham_gia),
            state="readonly", height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.cbb_nguoi.pack(fill="x")

        # Hàng 5 (2 cột): Ngày bắt đầu & Ngày kết thúc
        hang5 = tk.Frame(khung, bg=theme.MAU_THE)
        hang5.pack(fill="x", pady=(0, 10))
        hang5.columnconfigure(0, weight=1, uniform="h5")
        hang5.columnconfigure(1, weight=1, uniform="h5")

        f_bd = tk.Frame(hang5, bg=theme.MAU_THE)
        f_bd.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._nhan(f_bd, "Ngày bắt đầu (YYYY-MM-DD)")
        ctk.CTkEntry(
            f_bd, textvariable=self.var_bat_dau, height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        ).pack(fill="x")

        f_kt = tk.Frame(hang5, bg=theme.MAU_THE)
        f_kt.grid(row=0, column=1, sticky="ew")
        self._nhan(f_kt, "Ngày kết thúc (YYYY-MM-DD)")
        ctk.CTkEntry(
            f_kt, textvariable=self.var_ket_thuc, height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        ).pack(fill="x")

        # Hàng 6: Checkbox "Là công việc khẩn cấp (CongViecKhan)" chuẩn thiết kế Figma
        self.chk_khan = ctk.CTkCheckBox(
            khung, text="Là công việc khẩn cấp (CongViecKhan)",
            variable=self.var_khan_cap, command=self._khi_tick_khan_cap,
            font=theme.FONT_CHUAN, text_color=theme.MAU_CHU_NHAN,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            border_color=theme.MAU_VIEN_THE, corner_radius=4,
            checkbox_width=18, checkbox_height=18
        )
        self.chk_khan.pack(anchor="w", pady=(2, 8))

        # Hàng 7: Bình luận (khi đang sửa công việc)
        if self.cong_viec:
            self._dung_binh_luan(khung)

        # Đường kẻ phân cách & nút Hủy / Lưu công việc
        tk.Frame(khung, bg=theme.MAU_VIEN, height=1).pack(fill="x", pady=(8, 10))
        hang_nut = tk.Frame(khung, bg=theme.MAU_THE)
        hang_nut.pack(fill="x", side="bottom")

        ctk.CTkButton(
            hang_nut, text="Lưu công việc", command=self.luu,
            width=135, height=38, corner_radius=7,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            text_color="white", font=theme.FONT_DAM
        ).pack(side="right")

        ctk.CTkButton(
            hang_nut, text="Hủy", command=self.destroy,
            width=90, height=38, corner_radius=7,
            fg_color="white", hover_color=theme.MAU_NEN,
            border_width=1, border_color=theme.MAU_VIEN_THE,
            text_color=theme.MAU_CHU_NHAN, font=theme.FONT_DAM
        ).pack(side="right", padx=(0, 8))

    def _khi_tick_khan_cap(self):
        if self.var_khan_cap.get():
            self.var_uu_tien.set("Khẩn")
        elif self.var_uu_tien.get() == "Khẩn":
            self.var_uu_tien.set("Trung bình")

    def _khi_chon_uu_tien(self, gia_tri):
        self.var_khan_cap.set(gia_tri == "Khẩn")

    def _do_du_lieu_cu(self):
        cv = self.cong_viec
        self.var_ma.set(cv.ma_cong_viec)
        self.var_tieu_de.set(cv.tieu_de)
        self.txt_mo_ta.insert("1.0", cv.mo_ta or "")
        self.var_nguoi.set(cv.nguoi_phu_trach)
        self.var_nhan.set(cv.nhan)
        self.var_uu_tien.set(cv.muc_uu_tien)
        self.var_trang_thai.set(cv.trang_thai)
        self.var_bat_dau.set(cv.ngay_bat_dau)
        self.var_ket_thuc.set(cv.ngay_ket_thuc)
        self.var_khan_cap.set(cv.muc_uu_tien == "Khẩn")

        # Đổi cột phải đi qua chuyen_trang_thai() để có ghi nhật ký -> khóa ở đây
        self.cbb_trang_thai.configure(state="disabled")
        # CongViecKhan luôn là "Khẩn" nên không cho đổi
        if cv.muc_uu_tien == "Khẩn":
            self.cbb_uu_tien.configure(state="disabled")
            self.chk_khan.configure(state="disabled")

    # ------------------------------------------------------------ xử lý
    def _sinh_ma(self):
        """Sinh mã CV-xxx tiếp theo, ví dụ CV-009."""
        so = [int(cv.ma_cong_viec[3:]) for cv in self.du_an.cong_viec]
        return f"CV-{(max(so) + 1 if so else 1):03d}"

    def _kiem_tra_ngay(self, bat_dau, ket_thuc):
        """Trả về câu báo lỗi, hoặc None nếu hợp lệ."""
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
        tieu_de = self.var_tieu_de.get().strip()
        if not tieu_de or not self.var_nguoi.get():
            messagebox.showwarning("Thiếu thông tin",
                                   "Tiêu đề và người phụ trách không được để trống.",
                                   parent=self)
            return
        bat_dau = self.var_bat_dau.get().strip()
        ket_thuc = self.var_ket_thuc.get().strip()
        loi_ngay = self._kiem_tra_ngay(bat_dau, ket_thuc)
        if loi_ngay:
            messagebox.showwarning("Ngày không hợp lệ", loi_ngay, parent=self)
            return

        du_lieu = {
            "tieu_de": tieu_de,
            "mo_ta": self.txt_mo_ta.get("1.0", "end-1c").strip(),
            "nguoi_phu_trach": self.var_nguoi.get(),
            "nhan": self.var_nhan.get(),
            "ngay_bat_dau": bat_dau,
            "ngay_ket_thuc": ket_thuc,
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
                self.ql.tao_cong_viec(self.du_an, du_lieu)
        except KanbanException as loi:
            messagebox.showerror("Không lưu được", loi.thong_diep, parent=self)
            return

        self.destroy()
        if self.khi_xong:
            self.khi_xong()

    # ------------------------------------------------------------ bình luận
    def _dung_binh_luan(self, khung):
        kv = ctk.CTkFrame(khung, fg_color=theme.MAU_O_NHAP, corner_radius=8,
                          border_width=1, border_color=theme.MAU_VIEN)
        kv.pack(fill="x", pady=(4, 4))

        dau_bl = tk.Frame(kv, bg=theme.MAU_O_NHAP)
        dau_bl.pack(fill="x", padx=10, pady=(6, 4))
        tk.Label(dau_bl, text="Bình luận trao đổi", bg=theme.MAU_O_NHAP,
                 fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM).pack(side="left")
        ctk.CTkButton(
            dau_bl, text="Xóa bình luận đã chọn", command=self.xoa_binh_luan,
            width=140, height=24, corner_radius=5,
            fg_color="white", hover_color="#fee2e2",
            border_width=1, border_color=theme.MAU_VIEN_THE,
            text_color=theme.MAU_LOI, font=theme.FONT_NHO
        ).pack(side="right")

        khung_ds = tk.Frame(kv, bg=theme.MAU_O_NHAP)
        khung_ds.pack(fill="x", padx=10)
        self.lst_bl = tk.Listbox(
            khung_ds, height=4, font=theme.FONT_NHO, activestyle="none",
            bg="white", fg=theme.MAU_CHU, bd=1, relief="solid",
            highlightthickness=0, selectbackground=theme.MAU_CHINH_NHAT,
            selectforeground=theme.MAU_CHINH
        )
        thanh = ttk.Scrollbar(khung_ds, orient="vertical", command=self.lst_bl.yview)
        self.lst_bl.configure(yscrollcommand=thanh.set)
        self.lst_bl.pack(side="left", fill="x", expand=True)
        thanh.pack(side="right", fill="y")

        hang_gui = tk.Frame(kv, bg=theme.MAU_O_NHAP)
        hang_gui.pack(fill="x", padx=10, pady=(6, 8))
        self.var_bl = tk.StringVar()
        ent = ctk.CTkEntry(
            hang_gui, textvariable=self.var_bl, placeholder_text="Nhập nội dung bình luận...",
            height=32, corner_radius=6, fg_color="white",
            border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_NHO
        )
        ent.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ent.bind("<Return>", lambda e: self.gui_binh_luan())
        ctk.CTkButton(
            hang_gui, text="Gửi", command=self.gui_binh_luan,
            width=68, height=32, corner_radius=6,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            text_color="white", font=theme.FONT_DAM
        ).pack(side="right")

        self._nap_binh_luan()

    def _nap_binh_luan(self):
        self.lst_bl.delete(0, "end")
        for bl in self.cong_viec.danh_sach_binh_luan:
            self.lst_bl.insert("end", f"[{bl.thoi_gian}] {bl.nguoi_gui}: {bl.noi_dung}")
        self.lst_bl.see("end")

    def gui_binh_luan(self):
        noi_dung = self.var_bl.get().strip()
        if not noi_dung:
            messagebox.showwarning("Thiếu nội dung", "Hãy nhập nội dung bình luận.", parent=self)
            return
        try:
            self.ql.them_binh_luan_cong_viec(self.du_an, self.cong_viec.ma_cong_viec, noi_dung)
        except KanbanException as loi:
            messagebox.showerror("Không gửi được", loi.thong_diep, parent=self)
            return
        self.var_bl.set("")
        self._nap_binh_luan()

    def xoa_binh_luan(self):
        chon = self.lst_bl.curselection()
        if not chon:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một bình luận để xóa.", parent=self)
            return
        bl = self.cong_viec.danh_sach_binh_luan[chon[0]]
        if not messagebox.askyesno("Xác nhận xóa", "Xóa bình luận này?", parent=self):
            return
        try:
            self.ql.xoa_binh_luan_cong_viec(self.du_an, self.cong_viec.ma_cong_viec, bl.ma_binh_luan)
        except KanbanException as loi:
            messagebox.showerror("Không xóa được", loi.thong_diep, parent=self)
            return
        self._nap_binh_luan()
