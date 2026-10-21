"""Hộp thoại thêm / sửa công việc."""
import re
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk, messagebox

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

        self.title("Sửa công việc" if cong_viec else "Thêm công việc")
        self.configure(bg=theme.MAU_NEN)
        self.resizable(False, False)
        self.transient(master)

        hom_nay = date.today()
        self.var_tieu_de = tk.StringVar()
        self.var_nguoi = tk.StringVar()
        self.var_nhan = tk.StringVar(value=NHAN_HOP_LE[0])
        self.var_uu_tien = tk.StringVar(value="Trung bình")
        self.var_trang_thai = tk.StringVar(value=du_an.danh_sach_cot[0])
        self.var_bat_dau = tk.StringVar(value=hom_nay.isoformat())
        self.var_ket_thuc = tk.StringVar(value=(hom_nay + timedelta(days=7)).isoformat())

        self._dung_giao_dien()
        if cong_viec:
            self._do_du_lieu_cu()
        can_giua(self)
        self.ent_tieu_de.focus_set()
        self.bind("<Escape>", lambda e: self.destroy())
        self.wait_visibility()
        self.grab_set()          # chặn thao tác cửa sổ chính khi đang mở hộp thoại

    # ------------------------------------------------------------ giao diện
    def _dung_giao_dien(self):
        khung = ttk.Frame(self, padding=16)
        khung.pack(fill="both", expand=True)
        khung.columnconfigure(1, weight=1)

        def dong(hang, nhan, widget):
            ttk.Label(khung, text=nhan).grid(row=hang, column=0, sticky="nw",
                                             pady=5, padx=(0, 12))
            widget.grid(row=hang, column=1, sticky="ew", pady=5)

        self.ent_tieu_de = ttk.Entry(khung, textvariable=self.var_tieu_de, width=42)
        dong(0, "Tiêu đề *", self.ent_tieu_de)

        self.txt_mo_ta = tk.Text(khung, height=4, width=42, wrap="word",
                                 font=theme.FONT_CHUAN)
        dong(1, "Mô tả", self.txt_mo_ta)

        dong(2, "Người phụ trách *", ttk.Combobox(
            khung, textvariable=self.var_nguoi, state="readonly",
            values=list(self.du_an.thanh_vien_tham_gia)))
        dong(3, "Nhãn", ttk.Combobox(
            khung, textvariable=self.var_nhan, state="readonly", values=NHAN_HOP_LE))

        self.cbb_uu_tien = ttk.Combobox(khung, textvariable=self.var_uu_tien,
                                        state="readonly", values=MUC_UU_TIEN_HOP_LE)
        dong(4, "Mức ưu tiên", self.cbb_uu_tien)

        self.cbb_trang_thai = ttk.Combobox(khung, textvariable=self.var_trang_thai,
                                           state="readonly",
                                           values=list(self.du_an.danh_sach_cot))
        dong(5, "Cột", self.cbb_trang_thai)

        dong(6, "Ngày bắt đầu", ttk.Entry(khung, textvariable=self.var_bat_dau))
        dong(7, "Ngày kết thúc", ttk.Entry(khung, textvariable=self.var_ket_thuc))
        ttk.Label(khung, text="Định dạng ngày: YYYY-MM-DD",
                  foreground=theme.MAU_CHU_PHU, font=theme.FONT_NHO
                  ).grid(row=8, column=1, sticky="w")

        if self.cong_viec:
            self._dung_binh_luan(khung, 9)

        hang_nut = ttk.Frame(khung)
        hang_nut.grid(row=10, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(hang_nut, text="Hủy", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(hang_nut, text="Lưu", style="Chinh.TButton",
                   command=self.luu).pack(side="right")

    def _do_du_lieu_cu(self):
        cv = self.cong_viec
        self.var_tieu_de.set(cv.tieu_de)
        self.txt_mo_ta.insert("1.0", cv.mo_ta or "")
        self.var_nguoi.set(cv.nguoi_phu_trach)
        self.var_nhan.set(cv.nhan)
        self.var_uu_tien.set(cv.muc_uu_tien)
        self.var_trang_thai.set(cv.trang_thai)
        self.var_bat_dau.set(cv.ngay_bat_dau)
        self.var_ket_thuc.set(cv.ngay_ket_thuc)
        # Đổi cột phải đi qua chuyen_trang_thai() để có ghi nhật ký -> khóa ở đây
        self.cbb_trang_thai.configure(state="disabled")
        # CongViecKhan luôn là "Khẩn" nên không cho đổi
        if cv.muc_uu_tien == "Khẩn":
            self.cbb_uu_tien.configure(state="disabled")

    # ------------------------------------------------------------ xử lý
    def _sinh_ma(self):
        """Sinh mã CV-xxx tiếp theo, ví dụ CV-009."""
        so = [int(cv.ma_cong_viec[3:]) for cv in self.du_an.cong_viec]
        return f"CV-{(max(so) + 1 if so else 1):03d}"

    def _kiem_tra_ngay(self, bat_dau, ket_thuc):
        """Trả về câu báo lỗi, hoặc None nếu hợp lệ. Kiểm tra ở UI trước khi gọi backend."""
        for ten, gia_tri in (("Ngày bắt đầu", bat_dau), ("Ngày kết thúc", ket_thuc)):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", gia_tri):
                return f"{ten} phải có dạng YYYY-MM-DD (ví dụ 2026-10-25)."
            try:
                datetime.strptime(gia_tri, "%Y-%m-%d")
            except ValueError:
                return f"{ten} không tồn tại trong lịch."
        if ket_thuc < bat_dau:       # chuỗi ISO so sánh trực tiếp được
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
    def _dung_binh_luan(self, khung, hang):
        kv = ttk.LabelFrame(khung, text="Bình luận", padding=8)
        kv.grid(row=hang, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        kv.columnconfigure(0, weight=1)

        self.lst_bl = tk.Listbox(kv, height=5, width=55, font=theme.FONT_NHO,
                                 activestyle="none")
        thanh = ttk.Scrollbar(kv, orient="vertical", command=self.lst_bl.yview)
        self.lst_bl.configure(yscrollcommand=thanh.set)
        self.lst_bl.grid(row=0, column=0, columnspan=2, sticky="ew")
        thanh.grid(row=0, column=2, sticky="ns")

        self.var_bl = tk.StringVar()
        ent = ttk.Entry(kv, textvariable=self.var_bl)
        ent.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ent.bind("<Return>", lambda e: self.gui_binh_luan())
        ttk.Button(kv, text="Gửi", command=self.gui_binh_luan
                   ).grid(row=1, column=1, padx=(6, 0), pady=(6, 0))
        ttk.Button(kv, text="Xóa bình luận đã chọn", command=self.xoa_binh_luan
                   ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

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