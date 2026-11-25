from services.BoLuuTru import BoLuuTruBase, BoLuuTruMock
from services.XacThucService import XacThucService
from services.DuAnService import DuAnService
from services.CongViecService import CongViecService
from services.QuyTrinhService import QuyTrinhService
from models.DuAn import DuAn
from models.CongViec import CongViec


class QuanLyKanban:
    """
    Facade Controller: Lớp điều phối trung tâm của toàn bộ ứng dụng Kanban (Facade Pattern).
    
    TÍNH ĐÓNG GÓI & THIẾT KẾ HƯỚNG ĐỐI TƯỢNG (OOP Facade):
    - Tích hợp và điều phối các dịch vụ chuyên biệt:
      + `bo_luu_tru`: Quản lý tầng đọc/ghi dữ liệu JSON (Dependency Inversion).
      + `xac_thuc`: Quản lý phiên đăng nhập và phân quyền đa hình.
      + `du_an_service`: Quản lý các dự án và thành viên dự án.
      + `cong_viec_service`: Quản lý công việc, kéo chuyển cột, bình luận, lọc.
    - Cung cấp giao diện đồng nhất, trực quan cho tầng Giao diện (UI) hoặc Client sử dụng.
    """

    def __init__(self, bo_luu_tru=None, ten_file_du_lieu_moc=None):
        if bo_luu_tru is None or isinstance(bo_luu_tru, str):
            self.bo_luu_tru = BoLuuTruMock(
                ten_file_du_an=bo_luu_tru,
                ten_file_du_lieu_moc=ten_file_du_lieu_moc
            )
        else:
            self.bo_luu_tru = bo_luu_tru

        # Khởi tạo các sub-services chuyên trách
        self.xac_thuc = XacThucService()
        self.chat = None  # ChatClient (WebSocket) nếu chạy với --chat, None = ngoại tuyến
        self.du_an_service = DuAnService(self.bo_luu_tru, self.xac_thuc)
        self.cong_viec_service = CongViecService(self.du_an_service, self.xac_thuc, self.bo_luu_tru)
        self.quy_trinh = QuyTrinhService(self.du_an_service, self.xac_thuc, self.bo_luu_tru)

    # ==================== PROPERTIES TƯƠNG THÍCH ====================
    @property
    def danh_sach_du_an(self):
        return self.du_an_service.danh_sach_du_an

    @danh_sach_du_an.setter
    def danh_sach_du_an(self, value):
        self.du_an_service.danh_sach_du_an = value

    @property
    def nguoi_dung_hien_tai(self):
        return self.xac_thuc.nguoi_dung_hien_tai

    @nguoi_dung_hien_tai.setter
    def nguoi_dung_hien_tai(self, user):
        self.xac_thuc.nguoi_dung_hien_tai = user

    # ==================== XÁC THỰC & PHÂN QUYỀN ====================
    def dang_nhap(self, ten_dang_nhap: str, mat_khau: str):
        return self.xac_thuc.dang_nhap(ten_dang_nhap, mat_khau, self.bo_luu_tru)

    def dang_ky(self, ten_dang_nhap: str, mat_khau: str, ho_ten: str = "", email: str = ""):
        return self.xac_thuc.dang_ky(ten_dang_nhap, mat_khau, ho_ten, email, self.bo_luu_tru)

    def lay_danh_sach_nguoi_dung(self):
        return self.bo_luu_tru.doc_danh_sach_thanh_vien()

    def lay_nhat_ky(self):
        return self.bo_luu_tru.doc_nhat_ky()

    def dang_xuat(self):
        return self.xac_thuc.dang_xuat()

    def doi_mat_khau(self, mat_khau_cu: str, mat_khau_moi: str):
        """Đổi mật khẩu người dùng hiện tại và lưu xuống file."""
        nd = self.nguoi_dung_hien_tai
        if nd is None:
            from exceptions import KhongCoQuyenError
            raise KhongCoQuyenError("Bạn chưa đăng nhập vào hệ thống", hanh_dong="DOI_MAT_KHAU")
        nd.doi_mat_khau(mat_khau_cu, mat_khau_moi)
        danh_sach = self.bo_luu_tru.doc_danh_sach_thanh_vien()
        for i, tv in enumerate(danh_sach):
            if tv.ten_dang_nhap == nd.ten_dang_nhap:
                danh_sach[i] = nd
                break
        self.bo_luu_tru.ghi_danh_sach_thanh_vien(danh_sach)
        from logger import logger
        logger.info(f"Người dùng '{nd.ten_dang_nhap}' đã đổi mật khẩu thành công")
        return True

    def kiem_tra_quyen_du_an(self, du_an: DuAn, bat_loi: bool = False) -> bool:
        return self.xac_thuc.kiem_tra_quyen_du_an(du_an, bat_loi)

    def kiem_tra_quyen_cong_viec(self, cong_viec: CongViec, bat_loi: bool = False, du_an=None) -> bool:
        return self.xac_thuc.kiem_tra_quyen_cong_viec(cong_viec, bat_loi, du_an=du_an)

    # ==================== QUẢN LÝ DỰ ÁN ====================
    def lay_danh_sach_du_an(self):
        return self.du_an_service.danh_sach_du_an

    def tao_du_an(self, ma_du_an: str, ten_du_an: str, danh_sach_cot=None):
        return self.du_an_service.tao_du_an(ma_du_an, ten_du_an, danh_sach_cot)

    def tim_du_an_theo_ma(self, ma_du_an: str):
        return self.du_an_service.tim_du_an_theo_ma(ma_du_an)

    def tim_du_an_hoac_loi(self, ma_du_an: str) -> DuAn:
        return self.du_an_service.tim_du_an_hoac_loi(ma_du_an)

    def xoa_du_an(self, ma_du_an: str):
        return self.du_an_service.xoa_du_an(ma_du_an, self.nguoi_dung_hien_tai)

    def them_thanh_vien_du_an(self, du_an: DuAn, ten_dang_nhap: str):
        self.kiem_tra_quyen_du_an(du_an, bat_loi=True)
        return self.du_an_service.them_thanh_vien_du_an(du_an, ten_dang_nhap)

    def xoa_thanh_vien_du_an(self, du_an: DuAn, ten_dang_nhap: str):
        self.kiem_tra_quyen_du_an(du_an, bat_loi=True)
        return self.du_an_service.xoa_thanh_vien_du_an(du_an, ten_dang_nhap)

    def cap_quyen_truong_nhom(self, du_an: DuAn, ten_dang_nhap: str):
        from exceptions import KhongCoQuyenError, KhongTimThayError
        from models.NguoiDung.TruongNhom import TruongNhom
        if self.nguoi_dung_hien_tai is None or self.nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ admin được cấp quyền trưởng nhóm")
        ds = self.lay_danh_sach_nguoi_dung()
        nd = next((x for x in ds if x.ten_dang_nhap == ten_dang_nhap), None)
        if nd is None or ten_dang_nhap not in du_an.thanh_vien_tham_gia:
            raise KhongTimThayError("Tài khoản phải tham gia dự án trước khi làm trưởng nhóm")
        if nd.vai_tro != "truong_nhom":
            ds[ds.index(nd)] = TruongNhom(nd.ten_dang_nhap, nd._mat_khau, nd.ho_ten, nd.email, da_bam=True)
            self.bo_luu_tru.ghi_danh_sach_thanh_vien(ds)
        du_an.nhom.setdefault(ten_dang_nhap, [])
        self.du_an_service.luu_du_lieu()
        self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": "cap_leader", "ma_du_an": du_an.ma_du_an,
                                     "ten_dang_nhap": self.nguoi_dung_hien_tai.ten_dang_nhap,
                                     "thanh_vien": ten_dang_nhap})

    def tao_tai_khoan_truong_nhom(self, du_an, ten_dang_nhap, mat_khau, ho_ten="", email=""):
        from exceptions import KhongCoQuyenError
        if self.nguoi_dung_hien_tai is None or self.nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ admin được tạo tài khoản Leader")
        self.dang_ky(ten_dang_nhap, mat_khau, ho_ten, email)
        self.them_thanh_vien_du_an(du_an, ten_dang_nhap)
        self.cap_quyen_truong_nhom(du_an, ten_dang_nhap)

    def thu_hoi_quyen_truong_nhom(self, ten_dang_nhap):
        from exceptions import KhongCoQuyenError, DuLieuKhongHopLeError, KhongTimThayError
        from models.NguoiDung.ThanhVien import ThanhVien
        if self.nguoi_dung_hien_tai is None or self.nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ admin được thu hồi quyền Leader")
        if any(da.nhom.get(ten_dang_nhap) for da in self.danh_sach_du_an):
            raise DuLieuKhongHopLeError("Chuyển thành viên trong các nhóm trước khi thu hồi quyền")
        ds = self.lay_danh_sach_nguoi_dung()
        nd = next((x for x in ds if x.ten_dang_nhap == ten_dang_nhap), None)
        if nd is None or nd.vai_tro != "truong_nhom":
            raise KhongTimThayError("Không tìm thấy tài khoản Leader")
        moi = ThanhVien(nd.ten_dang_nhap, nd._mat_khau, nd.ho_ten, nd.email, da_bam=True)
        moi.bi_khoa = nd.bi_khoa
        ds[ds.index(nd)] = moi
        self.bo_luu_tru.ghi_danh_sach_thanh_vien(ds)
        for da in self.danh_sach_du_an:
            da.nhom.pop(ten_dang_nhap, None)
        self.du_an_service.luu_du_lieu()
        self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": "thu_hoi_leader", "ten_dang_nhap": self.nguoi_dung_hien_tai.ten_dang_nhap,
                                     "thanh_vien": ten_dang_nhap})

    def dat_khoa_tai_khoan(self, ten_dang_nhap, bi_khoa=True):
        from exceptions import KhongCoQuyenError, KhongTimThayError
        if self.nguoi_dung_hien_tai is None or self.nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ admin được khóa tài khoản")
        if ten_dang_nhap == self.nguoi_dung_hien_tai.ten_dang_nhap:
            raise KhongCoQuyenError("Không được tự khóa tài khoản admin đang dùng")
        ds = self.lay_danh_sach_nguoi_dung()
        nd = next((x for x in ds if x.ten_dang_nhap == ten_dang_nhap), None)
        if nd is None:
            raise KhongTimThayError("Không tìm thấy tài khoản")
        nd.bi_khoa = bool(bi_khoa)
        self.bo_luu_tru.ghi_danh_sach_thanh_vien(ds)
        self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": "khoa_tai_khoan" if bi_khoa else "mo_khoa_tai_khoan",
                                     "ten_dang_nhap": self.nguoi_dung_hien_tai.ten_dang_nhap,
                                     "thanh_vien": ten_dang_nhap})

    def gan_thanh_vien_nhom(self, du_an: DuAn, leader: str, thanh_vien: str):
        from exceptions import KhongCoQuyenError, DuLieuKhongHopLeError
        if self.nguoi_dung_hien_tai is None or self.nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ admin được phân nhóm")
        if leader not in du_an.nhom or thanh_vien not in du_an.thanh_vien_tham_gia:
            raise DuLieuKhongHopLeError("Leader hoặc thành viên chưa thuộc dự án")
        if thanh_vien in du_an.nhom or any(thanh_vien in ds for ds in du_an.nhom.values()):
            raise DuLieuKhongHopLeError("Mỗi thành viên chỉ thuộc một nhóm")
        du_an.nhom[leader].append(thanh_vien)
        try:
            self.du_an_service.luu_du_lieu()
        except Exception:
            du_an.nhom[leader].remove(thanh_vien)
            raise
        self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": "gan_nhom", "ma_du_an": du_an.ma_du_an,
                                     "ten_dang_nhap": self.nguoi_dung_hien_tai.ten_dang_nhap,
                                     "leader": leader, "thanh_vien": thanh_vien})

    def chuyen_thanh_vien_nhom(self, du_an: DuAn, thanh_vien: str, leader_moi: str = None):
        """Chuyển thành viên sang nhóm của leader mới, hoặc gỡ khỏi nhóm nếu leader_moi rỗng."""
        from exceptions import KhongCoQuyenError, DuLieuKhongHopLeError
        if self.nguoi_dung_hien_tai is None or self.nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ admin được chuyển nhóm thành viên")
        if thanh_vien not in du_an.thanh_vien_tham_gia or thanh_vien in du_an.nhom:
            raise DuLieuKhongHopLeError("Chỉ chuyển nhóm được cho thành viên thường thuộc dự án")
        leader_dich = (leader_moi or "").strip()
        if leader_dich and leader_dich not in du_an.nhom:
            raise DuLieuKhongHopLeError(f"Leader '{leader_dich}' chưa quản lý nhóm nào trong dự án")
        nhom_cu = {k: list(v) for k, v in du_an.nhom.items()}
        for ds in du_an.nhom.values():
            if thanh_vien in ds:
                ds.remove(thanh_vien)
        if leader_dich:
            du_an.nhom[leader_dich].append(thanh_vien)
        try:
            self.du_an_service.luu_du_lieu()
        except Exception:
            du_an.nhom = nhom_cu
            raise
        self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": "chuyen_nhom", "ma_du_an": du_an.ma_du_an,
                                     "ten_dang_nhap": self.nguoi_dung_hien_tai.ten_dang_nhap,
                                     "thanh_vien": thanh_vien, "leader_moi": leader_dich})

    # ==================== QUẢN LÝ CÔNG VIỆC ====================
    def tao_cong_viec(self, du_an: DuAn, du_lieu: dict, la_cong_viec_khan: bool = False):
        return self.cong_viec_service.tao_cong_viec(du_an, du_lieu, la_cong_viec_khan)

    def cap_nhat_cong_viec(self, du_an: DuAn, ma_cong_viec: str, du_lieu_moi: dict):
        return self.cong_viec_service.cap_nhat_cong_viec(du_an, ma_cong_viec, du_lieu_moi)

    def xoa_cong_viec(self, du_an: DuAn, ma_cong_viec: str):
        return self.quy_trinh.huy_cong_viec(du_an, ma_cong_viec, "Hủy từ giao diện")

    def huy_cong_viec(self, du_an, ma_cong_viec, ly_do):
        return self.quy_trinh.huy_cong_viec(du_an, ma_cong_viec, ly_do)

    def danh_dau_chua_hoan_thanh(self, du_an, ma_cong_viec, ly_do):
        return self.quy_trinh.danh_dau_chua_hoan_thanh(du_an, ma_cong_viec, ly_do)

    def khoi_phuc_cong_viec(self, du_an, ma_cong_viec):
        return self.quy_trinh.khoi_phuc_cong_viec(du_an, ma_cong_viec)

    def duyet_cong_viec(self, du_an, ma_cong_viec, chap_nhan=True):
        return self.quy_trinh.duyet_cong_viec(du_an, ma_cong_viec, chap_nhan)

    def gui_lai_cong_viec(self, du_an, ma_cong_viec):
        return self.quy_trinh.gui_lai_cong_viec(du_an, ma_cong_viec)

    def duyet_hoan_thanh(self, du_an, ma_cong_viec, chap_nhan=True, ly_do=""):
        return self.quy_trinh.duyet_hoan_thanh(du_an, ma_cong_viec, chap_nhan, ly_do)

    def yeu_cau_mo_lai(self, du_an, ma_cong_viec, ly_do):
        return self.quy_trinh.yeu_cau_mo_lai(du_an, ma_cong_viec, ly_do)

    def duyet_mo_lai(self, du_an, ma_cong_viec, chap_nhan=True):
        return self.quy_trinh.duyet_mo_lai(du_an, ma_cong_viec, chap_nhan)

    def yeu_cau_gia_han(self, du_an, ma_cong_viec, han_moi, ly_do):
        return self.quy_trinh.yeu_cau_gia_han(du_an, ma_cong_viec, han_moi, ly_do)

    def duyet_gia_han(self, du_an, ma_cong_viec, chap_nhan=True):
        return self.quy_trinh.duyet_gia_han(du_an, ma_cong_viec, chap_nhan)

    def chuyen_trang_thai(self, du_an: DuAn, ma_cong_viec: str, trang_thai_moi: str):
        return self.cong_viec_service.chuyen_trang_thai(du_an, ma_cong_viec, trang_thai_moi)

    # ==================== QUẢN LÝ BÌNH LUẬN ====================
    def them_binh_luan_cong_viec(self, du_an: DuAn, ma_cong_viec: str, noi_dung: str):
        return self.cong_viec_service.them_binh_luan_cong_viec(du_an, ma_cong_viec, noi_dung)

    def ap_dung_binh_luan_tu_xa(self, du_an: DuAn, ma_cong_viec: str, du_lieu_bl: dict):
        return self.cong_viec_service.ap_dung_binh_luan_tu_xa(du_an, ma_cong_viec, du_lieu_bl)

    def ap_dung_xoa_binh_luan_tu_xa(self, du_an: DuAn, ma_cong_viec: str, ma_binh_luan: str):
        return self.cong_viec_service.ap_dung_xoa_binh_luan_tu_xa(du_an, ma_cong_viec, ma_binh_luan)

    def xoa_binh_luan_cong_viec(self, du_an: DuAn, ma_cong_viec: str, ma_binh_luan: str):
        return self.cong_viec_service.xoa_binh_luan_cong_viec(du_an, ma_cong_viec, ma_binh_luan)

    # ==================== TÌM KIẾM & LỌC ====================
    def tim_kiem_cong_viec(self, du_an: DuAn, tu_khoa: str):
        return self.cong_viec_service.tim_kiem_cong_viec(du_an, tu_khoa)

    def loc_theo_thanh_vien(self, du_an: DuAn, ten_dang_nhap: str):
        return self.cong_viec_service.loc_theo_thanh_vien(du_an, ten_dang_nhap)

    def loc_theo_nhan(self, du_an: DuAn, ten_nhan: str):
        return self.cong_viec_service.loc_theo_nhan(du_an, ten_nhan)

    def loc_theo_muc_uu_tien(self, du_an: DuAn, muc_uu_tien: str):
        return self.cong_viec_service.loc_theo_muc_uu_tien(du_an, muc_uu_tien)


# Re-export để tương thích ngược nếu có file import BoLuuTru từ module QuanLyKaban
BoLuuTruBase = BoLuuTruBase
BoLuuTruMock = BoLuuTruMock
