"""MainWindow: Cửa sổ chính của ứng dụng Kanban điều phối Sidebar, Topbar và BoardView."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from models.CongViec.CongViecBase import TRANG_THAI_DANG_XU_LY
from exceptions import (
    KanbanException, KhongCoQuyenError, KhongTimThayError,
    LoiLuuTruError, DuLieuKhongHopLeError
)
from ui.styles import theme
from ui.components.sidebar import SidebarComponent
from ui.components.topbar import TopbarComponent, TAT_CA
from ui.views.board_view import BoardView
from ui.views.stats_view import StatsView
from ui.dialogs.task_dialog import TaskDialog
from ui.dialogs.column_dialog import TaoDuAnDialog, ThanhVienDuAnDialog
from ui.dialogs.confirm_dialog import xac_nhan
from ui.dialogs.doi_mat_khau_dialog import DoiMatKhauDialog
from config import SO_VIEC_API_TOI_DA
from services.nhap_api import nhap_cong_viec_tu_api

class MainWindow(tk.Toplevel):
    """
    Cửa sổ chính của ứng dụng Kanban:
    - Điều phối SidebarComponent, TopbarComponent, BoardView.
    - Đồng bộ dữ liệu với QuanLyKanban.
    - Hỗ trợ phím tắt, menu chuột phải, kéo thả task.
    """

    def __init__(self, goc, ql, khi_dang_xuat=None):
        super().__init__(goc)
        self.goc = goc
        self.ql = ql
        self.khi_dang_xuat_cb = khi_dang_xuat

        self.ds_du_an = []
        self.du_an = None
        self.cv_dang_chon = None
        self.the_dang_chon = None
        self._the_ma = None
        self._sap_xep_dao = {}

        self.title("Kanban Board — Quản lý công việc")
        self.geometry("1280x800")
        self.minsize(1050, 650)
        self.configure(bg=theme.MAU_NEN)

        self._khoi_tao_bien_trang_thai()
        self._dung_thanh_menu()
        self._dung_bo_cuc_chinh()
        self._tao_menu_chuot_phai()
        self._dang_ky_phim_tat()

        self._nap_du_an()
        self.protocol("WM_DELETE_WINDOW", self._khi_dong_cua_so)

    def _khoi_tao_bien_trang_thai(self):
        """Khởi tạo các biến theo dõi để liên kết component và tương thích ngược."""
        self.var_du_an = tk.StringVar(value="(Chưa có dự án)")
        self.var_tim_kiem, self.var_uu_tien = tk.StringVar(), tk.StringVar(value=TAT_CA)
        self.var_nhan, self.var_thanh_vien = tk.StringVar(value=TAT_CA), tk.StringVar(value=TAT_CA)
        self.var_loc_nhanh = tk.StringVar(value="tat_ca")
        self.ten_nguoi_map = {nd.ten_dang_nhap: nd.ho_ten for nd in self.ql.lay_danh_sach_nguoi_dung()}

    def _dung_thanh_menu(self):
        """Tạo menu bar chuẩn phía trên cửa sổ."""
        self.menubar = tk.Menu(self)
        self.configure(menu=self.menubar)

        m_ht = tk.Menu(self.menubar, tearoff=0)
        m_ht.add_command(label="Đăng xuất", command=self.dang_xuat)
        m_ht.add_separator()
        m_ht.add_command(label="Thoát", command=self.destroy)
        self.menubar.add_cascade(label="Hệ thống", menu=m_ht)

        m_da = tk.Menu(self.menubar, tearoff=0)
        m_da.add_command(label="Tạo dự án mới", command=self.tao_du_an)
        m_da.add_command(label="Quản lý thành viên", command=self.quan_ly_thanh_vien)
        m_da.add_separator()
        m_da.add_command(label="Xóa dự án hiện tại", command=self.xoa_du_an_hien_tai)
        self.menubar.add_cascade(label="Dự án", menu=m_da)

        m_cv = tk.Menu(self.menubar, tearoff=0)
        m_cv.add_command(label="Thêm công việc...", command=self.them_cong_viec)
        m_cv.add_command(label="Nhập công việc từ API...", command=self.nhap_tu_api)
        m_cv.add_separator()
        m_cv.add_command(label="Làm mới (F5)", command=self.ve_lai)
        self.menubar.add_cascade(label="Công việc", menu=m_cv)

    def _dung_bo_cuc_chinh(self):
        """Dựng khung Sidebar (trái) + Khung Làm việc (phải) với Topbar & BoardView."""
        # 1. Sidebar bên trái
        self.sidebar = SidebarComponent(
            self, self.ql, khi_chon_du_an=self._chon_du_an, khi_tao_du_an=self.tao_du_an,
            khi_chon_loc_nhanh=self._chon_loc_nhanh, khi_dang_xuat=self.dang_xuat,
            khi_thay_doi_trang_thai=lambda t: self.lbl_trang_thai.configure(text=t)
        )
        self.sidebar.pack(side="left", fill="y")
        self.nut_loc_nhanh = self.sidebar.nut_loc_nhanh

        # Splitter kéo giãn chiều rộng Sidebar
        self.splitter = tk.Frame(self, bg="#e2e8f0", width=4, cursor="sb_h_double_arrow")
        self.splitter.pack(side="left", fill="y")
        self._gan_su_kien_splitter()

        # 2. Khung làm việc chính bên phải
        self.khung_phai = tk.Frame(self, bg=theme.MAU_NEN)
        self.khung_phai.pack(side="left", fill="both", expand=True)

        # Statusbar ở đáy
        self.statusbar = tk.Frame(self.khung_phai, bg="#ffffff", height=24, highlightthickness=1, highlightbackground="#e2e8f0")
        self.statusbar.pack(side="bottom", fill="x")
        self.lbl_trang_thai = tk.Label(
            self.statusbar, text="Sẵn sàng.", bg="#ffffff",
            fg="#64748b", font=theme.FONT_NHO, anchor="w", padx=10
        )
        self.lbl_trang_thai.pack(side="left", fill="x", expand=True)

        # Topbar ở trên
        self.topbar = TopbarComponent(
            self.khung_phai, khi_them_viec=self.them_cong_viec,
            khi_bat_tat_hoat_dong=self.bat_tat_hoat_dong, khi_mo_thong_ke=self.mo_thong_ke,
            khi_ql_thanh_vien=self.quan_ly_thanh_vien, khi_xoa_du_an=self.xoa_du_an_hien_tai,
            khi_thay_doi_loc=self.ve_lai, khi_dat_lai_loc=self.ve_lai, khi_doi_che_do=self._doi_che_do_xem
        )
        self.topbar.pack(fill="x")

        # Ánh xạ thuộc tính tương thích ngược
        self.btn_them_cv = self.topbar.btn_them_cv
        self.btn_hoat_dong, self.btn_thong_ke = self.topbar.btn_hoat_dong, self.topbar.btn_thong_ke
        self.btn_thanh_vien, self.btn_xoa_da = self.topbar.btn_thanh_vien, self.topbar.btn_xoa_da
        self.btn_dat_lai = self.btn_xoa_loc = self.topbar.btn_dat_lai
        self.lbl_ten_da = self.topbar.lbl_ten_da
        self.cbb_du_an = ttk.Combobox(self, textvariable=self.var_du_an, state="readonly")
        self.cbb_tv, self.cbb_uu_tien = self.topbar.cbb_tv, self.topbar.cbb_uu_tien
        self.ent_tim = self.entry_tim = self.topbar.entry_tim
        self.thanh_tien_do, self.lbl_tien_do_nhanh = self.topbar.thanh_tien_do, self.topbar.lbl_tien_do
        self.lbl_dem_tong = self.lbl_dem_xong = self.lbl_dem_khan = self.lbl_so_luong_hien_thi = self.khung_avatars = tk.Label(self)

        # BoardView hiển thị Kanban + Danh sách + Ngăn kéo Hoạt động bên phải
        self.board_view = BoardView(
            self.khung_phai, khi_chon_task=self.chon_the, khi_mo_task=self.mo_the,
            khi_menu_task=self.hien_menu, khi_keo_task=self.khi_keo, khi_tha_task=self.khi_tha,
            khi_them_nhanh=self.them_cong_viec_tai_cot, khi_chuyen_nhanh=self.chuyen_nhanh_tiep_theo,
            khi_dong_hoat_dong=None
        )
        self.board_view.pack(fill="both", expand=True)

        self.cac_cot = self.board_view.cot_widgets
        self.cot_kanban = self.cac_cot
        self.drawer_hoat_dong = self.board_view.drawer_hoat_dong
        self.tree_ds = self.board_view.tree_ds
        self.khung_kpi = self.board_view.khung_kpi
        self.lbl_kpi_tong = self.board_view.lbl_kpis["tong"]
        self.lbl_kpi_dang_lam = self.board_view.lbl_kpis["dang_lam"]
        self.lbl_kpi_xong = self.board_view.lbl_kpis["xong"]
        self.lbl_kpi_khan = self.board_view.lbl_kpis["khan"]

        # Gắn sự kiện danh sách treeview
        self.tree_ds.bind("<<TreeviewSelect>>", self._khi_chon_dong_ds)
        self.tree_ds.bind("<Double-1>", lambda _e: self.mo_the(self.cv_dang_chon) if self.cv_dang_chon else None)
        self.tree_ds.bind("<Button-3>", self._khi_chuot_phai_ds)

    def _gan_su_kien_splitter(self):
        """Kéo chuột để co giãn chiều rộng Sidebar mượt mà."""
        self._splitter_keo = False
        self._splitter_x_dau = 0
        self._sidebar_w_dau = 218

        def _bam(e):
            self._splitter_keo = True
            self._splitter_x_dau = e.x_root
            self._sidebar_w_dau = self.sidebar.winfo_width()
            self.splitter.configure(bg="#6d669b")

        def _re(e):
            if not self._splitter_keo:
                return
            delta = e.x_root - self._splitter_x_dau
            w_moi = max(160, min(380, self._sidebar_w_dau + delta))
            self.sidebar.configure(width=w_moi)
            self.sidebar._tinh_chinh_nhan_du_an()

        def _tha(_e):
            self._splitter_keo = False
            self.splitter.configure(bg="#e2e8f0")

        self.splitter.bind("<Button-1>", _bam)
        self.splitter.bind("<B1-Motion>", _re)
        self.splitter.bind("<ButtonRelease-1>", _tha)

    def _tao_menu_chuot_phai(self):
        self.menu_phai = tk.Menu(self, tearoff=0)
        self.menu_phai.add_command(label="Xem / Sửa chi tiết", command=self.sua_dang_chon)
        self.menu_chuyen = tk.Menu(self.menu_phai, tearoff=0)
        self.menu_phai.add_cascade(label="Chuyển sang cột", menu=self.menu_chuyen)
        self.menu_phai.add_separator()
        self.menu_phai.add_command(label="Xóa công việc", command=self.xoa_dang_chon)

    def _dang_ky_phim_tat(self):
        self.bind("<Control-n>", lambda _e: self.them_cong_viec())
        self.bind("<Control-f>", lambda _e: self.topbar.entry_tim.focus_set())
        self.bind("<F5>", lambda _e: self.ve_lai())
        self.bind("<Delete>", lambda _e: self.xoa_dang_chon())
        self.bind("<Alt-Right>", lambda _e: self.chuyen_nhanh_tiep_theo(self.cv_dang_chon) if self.cv_dang_chon else None)
        self.bind("<Control-Shift-S>", lambda _e: self.mo_thong_ke())

    def _nap_du_an(self, chon_ma=None):
        """Tải danh sách dự án và vẽ lại giao diện."""
        self.ds_du_an = [d for d in self.ql.lay_danh_sach_du_an() if self.ql.kiem_tra_quyen_du_an(d)]
        if not self.ds_du_an:
            self.du_an = None
            self.var_du_an.set("(Chưa có dự án)")
            self.topbar.cap_nhat_tieu_de("", "Chưa có dự án nào")
            self.sidebar.cap_nhat_du_an([], None)
            self._cap_nhat_trang_thai_nut_du_an()
            self.ve_lai()
            return

        vi_tri = next((i for i, d in enumerate(self.ds_du_an) if d.ma_du_an == chon_ma), 0)
        self.du_an = self.ds_du_an[vi_tri]
        self.var_du_an.set(f"{self.du_an.ma_du_an} - {self.du_an.ten_du_an}")

        self.topbar.cap_nhat_tieu_de(self.du_an.ma_du_an, self.du_an.ten_du_an)
        self.sidebar.cap_nhat_du_an(self.ds_du_an, self.du_an.ma_du_an)

        # Cập nhật danh sách thành viên trong topbar
        nd_map = {nd.ten_dang_nhap: nd for nd in self.ql.lay_danh_sach_nguoi_dung()}
        ds_tv_objs = [nd_map[u] for u in self.du_an.thanh_vien_tham_gia if u in nd_map]
        self.topbar.cap_nhat_thanh_vien(ds_tv_objs)

        # Dựng cột Kanban trong BoardView
        self.board_view.dung_cac_cot(self.du_an.danh_sach_cot, self.ten_nguoi_map)
        self.cac_cot = self.board_view.cot_widgets
        self.cot_kanban = self.cac_cot

        self._cap_nhat_trang_thai_nut_du_an()
        self.ve_lai()

    def _chon_du_an(self, ma_da):
        self._nap_du_an(chon_ma=ma_da)

    def _chon_loc_nhanh(self, ma_loc):
        self.var_loc_nhanh.set(ma_loc)
        self.sidebar.cap_nhat_loc_nhanh(ma_loc)
        self.ve_lai()

    def _cap_nhat_trang_thai_nut_du_an(self):
        co_da = self.du_an is not None
        la_qt = bool(self.ql.nguoi_dung_hien_tai and self.ql.nguoi_dung_hien_tai.vai_tro == "quan_tri")
        self.btn_them_cv.configure(state="normal" if co_da else "disabled")
        self.btn_thong_ke.configure(state="normal" if co_da else "disabled")
        self.btn_thanh_vien.configure(state="normal" if (co_da and la_qt) else "disabled")
        self.btn_xoa_da.configure(state="normal" if (co_da and la_qt) else "disabled")

    def _cong_viec_sau_loc(self):
        if not self.du_an:
            return []
        ql, da = self.ql, self.du_an
        kq = ql.tim_kiem_cong_viec(da, self.topbar.var_tim_kiem.get())

        che_do = self.var_loc_nhanh.get()
        if che_do == "cua_toi":
            nd = self.ql.nguoi_dung_hien_tai
            kq = [cv for cv in kq if cv.nguoi_phu_trach == (nd.ten_dang_nhap if nd else "")]
        elif che_do == "khan_cap":
            kq = [cv for cv in kq if cv.can_chu_y()]
        elif che_do == "hoan_thanh":
            kq = [cv for cv in kq if cv.is_hoan_thanh()]

        ut = self.topbar.var_uu_tien.get()
        if ut != TAT_CA:
            ds_ut = {cv.ma_cong_viec for cv in ql.loc_theo_muc_uu_tien(da, ut)}
            kq = [cv for cv in kq if cv.ma_cong_viec in ds_ut]

        tv_str = self.topbar.var_thanh_vien.get()
        if tv_str != TAT_CA:
            tv_ma = tv_str.split(" - ")[0].strip()
            ds_tv = {cv.ma_cong_viec for cv in ql.loc_theo_thanh_vien(da, tv_ma)}
            kq = [cv for cv in kq if cv.ma_cong_viec in ds_tv]

        return kq

    def ve_lai(self):
        """Vẽ lại toàn bộ thẻ công việc, danh sách treeview và KPI."""
        if not self.du_an:
            self.board_view.cap_nhat_kpi(0, 0, 0, 0)
            self.topbar.cap_nhat_tien_do(0, 0)
            return

        cv_hien_thi = self._cong_viec_sau_loc()
        for ten, cot in self.cac_cot.items():
            cot.hien_thi([cv for cv in cv_hien_thi if cv.trang_thai == ten])

        tong = len(self.du_an.cong_viec)
        xong = sum(1 for c in self.du_an.cong_viec if c.is_hoan_thanh())
        dang_lam = sum(1 for c in self.du_an.cong_viec if c.trang_thai in TRANG_THAI_DANG_XU_LY)
        khan     = sum(1 for c in self.du_an.cong_viec if c.can_chu_y())
        self.board_view.cap_nhat_kpi(tong, dang_lam, xong, khan)
        self.topbar.cap_nhat_tien_do(tong, xong)
        self._cap_nhat_tree_danh_sach(cv_hien_thi)

        if self.drawer_hoat_dong.winfo_ismapped():
            ds_nk = self.ql.lay_nhat_ky()
            self.board_view.cap_nhat_hoat_dong(ds_nk)

        self.lbl_trang_thai.configure(
            text=f"Dự án '{self.du_an.ten_du_an}': {len(cv_hien_thi)}/{tong} công việc."
        )

    def _cap_nhat_tree_danh_sach(self, ds_cv):
        self.tree_ds.delete(*self.tree_ds.get_children())
        for cv in ds_cv:
            ten_tv = self.ten_nguoi_map.get(cv.nguoi_phu_trach, cv.nguoi_phu_trach)
            self.tree_ds.insert(
                "", "end", iid=cv.ma_cong_viec,
                values=(cv.ma_cong_viec, cv.tieu_de, cv.trang_thai,
                        cv.muc_uu_tien, ten_tv, cv.ngay_ket_thuc, cv.canh_bao())
            )

    def _doi_che_do_xem(self, che_do):
        self.board_view.chuyen_che_do(che_do)
        self.ve_lai()

    def bat_tat_hoat_dong(self):
        mo = self.board_view.bat_tat_hoat_dong()
        if mo and self.du_an:
            ds_nk = self.ql.lay_nhat_ky()
            self.board_view.cap_nhat_hoat_dong(ds_nk)

    def chon_the(self, cv, card):
        for c in self.cac_cot.values():
            for t in c.cac_the.values():
                t.chon(False)
        self.cv_dang_chon = cv
        self.the_dang_chon = card
        if card:
            card.chon(True)

    def mo_the(self, cv):
        self.cv_dang_chon = cv
        TaskDialog(self, self.ql, self.du_an, cv, khi_xong=self.ve_lai)

    def hien_menu(self, cv, event):
        self.cv_dang_chon = cv
        self.menu_chuyen.delete(0, "end")
        for cot in self.du_an.danh_sach_cot:
            if cot != cv.trang_thai:
                self.menu_chuyen.add_command(
                    label=cot, command=lambda c=cot: self.chuyen_cot(cv, c)
                )
        self.menu_phai.tk_popup(event.x_root, event.y_root)

    def them_cong_viec(self):
        if not self.du_an:
            return
        TaskDialog(self, self.ql, self.du_an, khi_xong=self.ve_lai)
    def nhap_tu_api(self):
        """Lấy công việc mẫu từ API công khai, làm sạch, lưu JSON rồi thêm vào dự án đang mở."""
        if not self.du_an:
            messagebox.showinfo("Chưa có dự án", "Hãy chọn hoặc tạo dự án trước khi nhập từ API.", parent=self)
            return
        so = simpledialog.askinteger(
            "Nhập từ API", f"Số công việc muốn nhập (1–{SO_VIEC_API_TOI_DA}):",
            parent=self, minvalue=1, maxvalue=SO_VIEC_API_TOI_DA, initialvalue=5
        )
        if so is None:          # người dùng bấm Cancel
            return

        self.lbl_trang_thai.configure(text="Đang tải dữ liệu từ API...")
        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            kq = nhap_cong_viec_tu_api(self.ql, self.du_an, so)
        except Exception as loi:   # lỗi ngoài dự kiến: báo cho người dùng, không để ứng dụng dừng đột ngột
            messagebox.showerror("Lỗi hệ thống", f"Không thể nhập từ API: {loi}", parent=self)
            return
        finally:
            self.configure(cursor="")

        if kq["thong_bao"]:     # lỗi mạng, JSON sai cấu trúc, không ghi được file...
            messagebox.showwarning("Không nhập được từ API", kq["thong_bao"], parent=self)
        else:
            messagebox.showinfo(
                "Nhập từ API",
                f"Đã thêm {kq['them']} công việc.\nBỏ qua {kq['trung']} việc đã nhập trước đó.\n"
                f"Lỗi: {kq['loi']}.\n\nNguồn: dummyjson.com (đã lưu vào data/api_todos.json)",
                parent=self
            )
        self.ve_lai()
    def them_cong_viec_tai_cot(self, ten_cot):
        if not self.du_an:
            return
        TaskDialog(self, self.ql, self.du_an, khi_xong=self.ve_lai, trang_thai_mac_dinh=ten_cot)

    def sua_dang_chon(self):
        if self.cv_dang_chon:
            self.mo_the(self.cv_dang_chon)

    def xoa_dang_chon(self):
        if not self.cv_dang_chon:
            return
        if not self.ql.nguoi_dung_hien_tai.co_quyen_xoa_cong_viec():
            messagebox.showwarning("Không có quyền", "Chỉ Quản trị viên mới được xóa công việc.", parent=self)
            return
        if not xac_nhan(self, f"Xóa vĩnh viễn công việc '{self.cv_dang_chon.ma_cong_viec}'?"):
            return
        try:
            self.ql.xoa_cong_viec(self.du_an, self.cv_dang_chon.ma_cong_viec)
        except KhongCoQuyenError as loi:
            messagebox.showerror("Từ chối quyền", loi.thong_diep, parent=self)
            return
        except LoiLuuTruError as loi:
            messagebox.showerror("Lỗi lưu trữ", loi.thong_diep, parent=self)
            return
        except KanbanException as loi:
            messagebox.showerror("Lỗi xóa việc", loi.thong_diep, parent=self)
            return
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể xóa công việc: {e}", parent=self)
            return
        self.cv_dang_chon = None
        self.ve_lai()

    def chuyen_cot(self, cv, cot_dich):
        try:
            self.ql.chuyen_trang_thai(self.du_an, cv.ma_cong_viec, cot_dich)
        except KhongCoQuyenError as loi:
            messagebox.showerror("Từ chối quyền", loi.thong_diep, parent=self)
            return
        except (DuLieuKhongHopLeError, KhongTimThayError) as loi:
            messagebox.showwarning("Không hợp lệ", loi.thong_diep, parent=self)
            return
        except LoiLuuTruError as loi:
            messagebox.showerror("Lỗi lưu trữ", loi.thong_diep, parent=self)
            return
        except KanbanException as loi:
            messagebox.showerror("Lỗi chuyển cột", loi.thong_diep, parent=self)
            return
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể chuyển trạng thái: {e}", parent=self)
            return
        self.ve_lai()

    def chuyen_nhanh_tiep_theo(self, cv):
        ds_cot = self.du_an.danh_sach_cot
        if cv.trang_thai in ds_cot:
            idx = ds_cot.index(cv.trang_thai)
            if idx < len(ds_cot) - 1:
                self.chuyen_cot(cv, ds_cot[idx + 1])

    def khi_keo(self, cv, event):
        dich = self._cot_duoi_chuot(event)
        for ten, cot in self.cac_cot.items():
            cot.to_sang(ten == dich and ten != cv.trang_thai)

    def khi_tha(self, cv, event):
        for cot in self.cac_cot.values():
            cot.to_sang(False)
        dich = self._cot_duoi_chuot(event)
        if dich and dich != cv.trang_thai:
            self.after(10, lambda: self.chuyen_cot(cv, dich))

    def _cot_duoi_chuot(self, event):
        for ten, cot in self.cac_cot.items():
            if cot.chua_diem(event.x_root, event.y_root):
                return ten
        return None

    def _khi_chon_dong_ds(self, _event=None):
        sel = self.tree_ds.selection()
        if sel and self.du_an:
            self.cv_dang_chon = self.du_an.tim_cong_viec_theo_ma(sel[0])

    def _khi_chuot_phai_ds(self, event):
        row_id = self.tree_ds.identify_row(event.y)
        if row_id:
            self.tree_ds.selection_set(row_id)
            self._khi_chon_dong_ds()
            if self.cv_dang_chon:
                self.hien_menu(self.cv_dang_chon, event)

    def tao_du_an(self):
        TaoDuAnDialog(self, self.ql, khi_xong=lambda d: self._nap_du_an(chon_ma=d.ma_du_an))

    def quan_ly_thanh_vien(self):
        if self.du_an:
            ThanhVienDuAnDialog(self, self.ql, self.du_an, khi_xong=lambda: self._nap_du_an(chon_ma=self.du_an.ma_du_an))

    def xoa_du_an_hien_tai(self):
        if not self.du_an:
            return
        if not self.ql.nguoi_dung_hien_tai.co_quyen_xoa_du_an():
            messagebox.showwarning("Không có quyền", "Chỉ Quản trị viên mới được xóa dự án.", parent=self)
            return
        if not xac_nhan(self, f"Xóa toàn bộ dự án '{self.du_an.ma_du_an} — {self.du_an.ten_du_an}'?"):
            return
        try:
            self.ql.xoa_du_an(self.du_an.ma_du_an)
        except KhongCoQuyenError as loi:
            messagebox.showerror("Từ chối quyền", loi.thong_diep, parent=self)
            return
        except LoiLuuTruError as loi:
            messagebox.showerror("Lỗi lưu trữ", loi.thong_diep, parent=self)
            return
        except KanbanException as loi:
            messagebox.showerror("Lỗi xóa dự án", loi.thong_diep, parent=self)
            return
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể xóa dự án: {e}", parent=self)
            return
        self._nap_du_an()

    def mo_thong_ke(self):
        if self.du_an:
            StatsView(self, self.du_an, self.ql)

    def dang_xuat(self):
        self.destroy()
        if self.khi_dang_xuat_cb:
            self.khi_dang_xuat_cb()

    def _khi_dong_cua_so(self):
        self.destroy()
        if self.goc and self.goc.winfo_exists():
            self.goc.destroy()
