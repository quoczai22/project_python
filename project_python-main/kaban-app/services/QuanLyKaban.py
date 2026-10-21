from services.BoLuuTru import BoLuuTruBase, BoLuuTruMock
from services.XacThucService import XacThucService
from services.DuAnService import DuAnService
from services.CongViecService import CongViecService
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
        self.du_an_service = DuAnService(self.bo_luu_tru)
        self.cong_viec_service = CongViecService(self.du_an_service, self.xac_thuc, self.bo_luu_tru)

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

    def dang_xuat(self):
        return self.xac_thuc.dang_xuat()

    def kiem_tra_quyen_du_an(self, du_an: DuAn, bat_loi: bool = False) -> bool:
        return self.xac_thuc.kiem_tra_quyen_du_an(du_an, bat_loi)

    def kiem_tra_quyen_cong_viec(self, cong_viec: CongViec, bat_loi: bool = False) -> bool:
        return self.xac_thuc.kiem_tra_quyen_cong_viec(cong_viec, bat_loi)

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

    # ==================== QUẢN LÝ CÔNG VIỆC ====================
    def tao_cong_viec(self, du_an: DuAn, du_lieu: dict, la_cong_viec_khan: bool = False):
        return self.cong_viec_service.tao_cong_viec(du_an, du_lieu, la_cong_viec_khan)

    def cap_nhat_cong_viec(self, du_an: DuAn, ma_cong_viec: str, du_lieu_moi: dict):
        return self.cong_viec_service.cap_nhat_cong_viec(du_an, ma_cong_viec, du_lieu_moi)

    def xoa_cong_viec(self, du_an: DuAn, ma_cong_viec: str):
        return self.cong_viec_service.xoa_cong_viec(du_an, ma_cong_viec)

    def chuyen_trang_thai(self, du_an: DuAn, ma_cong_viec: str, trang_thai_moi: str):
        return self.cong_viec_service.chuyen_trang_thai(du_an, ma_cong_viec, trang_thai_moi)

    # ==================== QUẢN LÝ BÌNH LUẬN ====================
    def them_binh_luan_cong_viec(self, du_an: DuAn, ma_cong_viec: str, noi_dung: str):
        return self.cong_viec_service.them_binh_luan_cong_viec(du_an, ma_cong_viec, noi_dung)

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
