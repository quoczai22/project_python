import re
from models.NguoiDung import NguoiDung, ThanhVien
from exceptions import (
    KhongTimThayError, XacThucThatBaiError, KhongCoQuyenError,
    DuLieuKhongHopLeError, XungDotDuLieuError, LoiLuuTruError
)
from config import MAT_KHAU_TOI_THIEU, MAU_TEN_DANG_NHAP, MAU_EMAIL
from logger import logger

_REGEX_TEN_DANG_NHAP = re.compile(MAU_TEN_DANG_NHAP)
_REGEX_EMAIL = re.compile(MAU_EMAIL)


class XacThucService:
    """
    Dịch vụ quản lý xác thực đăng nhập và phiên làm việc của người dùng.
    """

    def __init__(self):
        self._nguoi_dung_hien_tai: NguoiDung = None

    @property
    def nguoi_dung_hien_tai(self) -> NguoiDung:
        return self._nguoi_dung_hien_tai

    @nguoi_dung_hien_tai.setter
    def nguoi_dung_hien_tai(self, user: NguoiDung):
        self._nguoi_dung_hien_tai = user

    def dang_nhap(self, ten_dang_nhap: str, mat_khau: str, bo_luu_tru):
        """Xác thực đăng nhập người dùng; ném ngoại lệ chuẩn xác khi thất bại."""
        danh_sach_thanh_vien = bo_luu_tru.doc_danh_sach_thanh_vien()

        thanh_vien = next(
            (tv for tv in danh_sach_thanh_vien if tv.ten_dang_nhap == ten_dang_nhap),
            None
        )
        if thanh_vien is None:
            raise KhongTimThayError(
                f"Tài khoản '{ten_dang_nhap}' không tồn tại trong hệ thống",
                loai_tai_nguyen="ThanhVien",
                khoa_tim_kiem=ten_dang_nhap
            )

        if getattr(thanh_vien, "bi_khoa", False):
            raise XacThucThatBaiError("Tài khoản đã bị khóa")

        if not thanh_vien.kiem_tra_mat_khau(mat_khau):
            raise XacThucThatBaiError("Mật khẩu không chính xác")

        self._nguoi_dung_hien_tai = thanh_vien
        logger.info(f"Người dùng '{ten_dang_nhap}' ({thanh_vien.vai_tro}) đã đăng nhập thành công")
        return self._nguoi_dung_hien_tai

    def dang_ky(self, ten_dang_nhap: str, mat_khau: str, ho_ten: str, email: str, bo_luu_tru):
        """
        Tạo tài khoản mới (luôn là vai trò 'thanh_vien', không cho tự đăng ký quản trị).
        Kiểm tra: tên đăng nhập hợp lệ + không trùng, mật khẩu đủ dài, email đúng regex + không trùng.
        Ném DuLieuKhongHopLeError / XungDotDuLieuError / LoiLuuTruError; thành công trả về ThanhVien mới.
        """
        ten_dang_nhap = (ten_dang_nhap or "").strip()
        ho_ten = (ho_ten or "").strip()
        email = (email or "").strip()
        mat_khau = mat_khau or ""

        if not _REGEX_TEN_DANG_NHAP.fullmatch(ten_dang_nhap):
            raise DuLieuKhongHopLeError(
                "Tên đăng nhập gồm 3-20 ký tự: chữ không dấu, số hoặc dấu gạch dưới",
                truong_loi="ten_dang_nhap", gia_tri=ten_dang_nhap
            )
        if len(mat_khau) < MAT_KHAU_TOI_THIEU:
            raise DuLieuKhongHopLeError(
                f"Mật khẩu phải có ít nhất {MAT_KHAU_TOI_THIEU} ký tự",
                truong_loi="mat_khau"
            )
        if email and not _REGEX_EMAIL.fullmatch(email):
            raise DuLieuKhongHopLeError(
                "Email không đúng định dạng (ví dụ: ten@gmail.com)",
                truong_loi="email", gia_tri=email
            )

        danh_sach = bo_luu_tru.doc_danh_sach_thanh_vien()
        if any(tv.ten_dang_nhap.lower() == ten_dang_nhap.lower() for tv in danh_sach):
            raise XungDotDuLieuError(
                f"Tên đăng nhập '{ten_dang_nhap}' đã tồn tại",
                khoa_trung="ten_dang_nhap", gia_tri=ten_dang_nhap
            )
        if email and any((tv.email or "").lower() == email.lower() for tv in danh_sach):
            raise XungDotDuLieuError(
                f"Email '{email}' đã được dùng cho tài khoản khác",
                khoa_trung="email", gia_tri=email
            )

        thanh_vien_moi = ThanhVien(ten_dang_nhap, mat_khau, ho_ten, email)  # mật khẩu được băm SHA-256 ở đây
        try:
            bo_luu_tru.ghi_danh_sach_thanh_vien(danh_sach + [thanh_vien_moi])
        except LoiLuuTruError:
            logger.error(f"Không thể lưu tài khoản mới '{ten_dang_nhap}'")
            raise
        except Exception as err:
            logger.error(f"Không thể lưu tài khoản mới '{ten_dang_nhap}': {err}")
            raise LoiLuuTruError(f"Không thể lưu tài khoản mới: {err}", loi_goc=err)

        logger.info(f"Đã tạo tài khoản mới '{ten_dang_nhap}' (thanh_vien)")
        return thanh_vien_moi

    def dang_xuat(self):
        """Đăng xuất tài khoản hiện tại."""
        user = self._nguoi_dung_hien_tai
        self._nguoi_dung_hien_tai = None
        if user:
            logger.info(f"Người dùng '{user.ten_dang_nhap}' đã đăng xuất")

    def kiem_tra_quyen_du_an(self, du_an, bat_loi: bool = False) -> bool:
        """ĐA HÌNH: Kiểm tra quyền truy cập dự án của người dùng hiện tại."""
        if self._nguoi_dung_hien_tai is None:
            if bat_loi:
                raise KhongCoQuyenError("Bạn chưa đăng nhập vào hệ thống", hanh_dong="TRUY_CAP_DU_AN")
            return False

        co_quyen = self._nguoi_dung_hien_tai.kiem_tra_quyen_du_an(du_an)
        if not co_quyen and bat_loi:
            raise KhongCoQuyenError(
                f"Người dùng '{self._nguoi_dung_hien_tai.ten_dang_nhap}' không có quyền truy cập dự án '{getattr(du_an, 'ma_du_an', '')}'",
                nguoi_dung=self._nguoi_dung_hien_tai.ten_dang_nhap,
                hanh_dong="TRUY_CAP_DU_AN"
            )
        return co_quyen

    def kiem_tra_quyen_cong_viec(self, cong_viec, bat_loi: bool = False, du_an=None) -> bool:
        """ĐA HÌNH: Kiểm tra quyền thao tác trên công việc của người dùng hiện tại."""
        if self._nguoi_dung_hien_tai is None:
            if bat_loi:
                raise KhongCoQuyenError("Bạn chưa đăng nhập vào hệ thống", hanh_dong="THAO_TAC_CONG_VIEC")
            return False

        co_quyen = self._nguoi_dung_hien_tai.kiem_tra_quyen_cong_viec(cong_viec)
        if (not co_quyen and du_an is not None
                and self._nguoi_dung_hien_tai.vai_tro == "truong_nhom"
                and getattr(cong_viec, "nguoi_phu_trach", None) in du_an.nhom.get(self._nguoi_dung_hien_tai.ten_dang_nhap, [])):
            co_quyen = True
        if not co_quyen and bat_loi:
            raise KhongCoQuyenError(
                f"Người dùng '{self._nguoi_dung_hien_tai.ten_dang_nhap}' không có quyền thao tác trên công việc '{getattr(cong_viec, 'ma_cong_viec', '')}'",
                nguoi_dung=self._nguoi_dung_hien_tai.ten_dang_nhap,
                hanh_dong="THAO_TAC_CONG_VIEC"
            )
        return co_quyen

    def co_quyen_xoa(self) -> bool:
        """Kiểm tra quyền xóa (chỉ quản trị viên có quyền)."""
        if self._nguoi_dung_hien_tai is None:
            return False
        return self._nguoi_dung_hien_tai.co_quyen_xoa_cong_viec()

    @staticmethod
    def _kiem_tra_ho_ten_email(ho_ten, email, danh_sach, bo_qua_ten):
        ho_ten_s = str(ho_ten or "").strip()
        email_s = str(email or "").strip()
        if email_s and not re.fullmatch(MAU_EMAIL, email_s):
            raise DuLieuKhongHopLeError(
                f"Email '{email_s}' không đúng định dạng",
                truong_loi="email", gia_tri=email_s
            )
        if email_s and any(
            tv.ten_dang_nhap.lower() != bo_qua_ten.lower()
            and (tv.email or "").lower() == email_s.lower()
            for tv in danh_sach
        ):
            raise XungDotDuLieuError(
                f"Email '{email_s}' đã được dùng cho tài khoản khác",
                khoa_trung="email", gia_tri=email_s
            )
        return ho_ten_s, email_s

    def sua_thong_tin_nguoi_dung(self, bo_luu_tru, ten_dang_nhap: str, ho_ten=None, email=None):
        """Admin sửa trực tiếp họ tên, email của bất kỳ tài khoản nào (không đổi username/vai trò)."""
        if self._nguoi_dung_hien_tai is None or self._nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ quản trị viên mới được sửa trực tiếp thông tin người dùng")
        danh_sach = bo_luu_tru.doc_danh_sach_thanh_vien()
        nd = next((tv for tv in danh_sach if tv.ten_dang_nhap == ten_dang_nhap), None)
        if nd is None:
            raise KhongTimThayError(f"Không tìm thấy tài khoản '{ten_dang_nhap}'", loai_tai_nguyen="ThanhVien", khoa_tim_kiem=ten_dang_nhap)
        ho_ten_moi = nd.ho_ten if ho_ten is None else ho_ten
        email_moi = nd.email if email is None else email
        ho_ten_s, email_s = self._kiem_tra_ho_ten_email(ho_ten_moi, email_moi, danh_sach, nd.ten_dang_nhap)
        cu_ten, cu_email = nd.ho_ten, nd.email
        nd.ho_ten, nd.email = ho_ten_s, email_s
        try:
            bo_luu_tru.ghi_danh_sach_thanh_vien(danh_sach)
        except Exception as err:
            nd.ho_ten, nd.email = cu_ten, cu_email
            raise LoiLuuTruError(f"Không lưu được thông tin người dùng: {err}", loi_goc=err)
        if self._nguoi_dung_hien_tai.ten_dang_nhap == nd.ten_dang_nhap:
            self._nguoi_dung_hien_tai.ho_ten, self._nguoi_dung_hien_tai.email = ho_ten_s, email_s
        bo_luu_tru.ghi_nhat_ky({
            "hanh_dong": "sua_thong_tin_nguoi_dung",
            "ten_dang_nhap": self._nguoi_dung_hien_tai.ten_dang_nhap,
            "thanh_vien": nd.ten_dang_nhap,
            "chi_tiet": f"{ho_ten_s} | {email_s}",
        })
        return nd

    def yeu_cau_sua_thong_tin(self, bo_luu_tru, ho_ten: str, email: str):
        """Leader/thành viên gửi yêu cầu sửa họ tên, email của chính mình (chờ admin duyệt)."""
        from datetime import datetime
        if self._nguoi_dung_hien_tai is None:
            raise KhongCoQuyenError("Bạn chưa đăng nhập vào hệ thống")
        danh_sach = bo_luu_tru.doc_danh_sach_thanh_vien()
        nd = next((tv for tv in danh_sach if tv.ten_dang_nhap == self._nguoi_dung_hien_tai.ten_dang_nhap), None)
        if nd is None:
            raise KhongTimThayError("Không tìm thấy tài khoản hiện tại")
        if nd.yeu_cau_sua_thong_tin:
            raise DuLieuKhongHopLeError("Bạn đã có một yêu cầu sửa thông tin đang chờ duyệt")
        ho_ten_s, email_s = self._kiem_tra_ho_ten_email(ho_ten, email, danh_sach, nd.ten_dang_nhap)
        yc = {"ho_ten": ho_ten_s, "email": email_s, "thoi_gian": datetime.now().isoformat()}
        nd.yeu_cau_sua_thong_tin = yc
        try:
            bo_luu_tru.ghi_danh_sach_thanh_vien(danh_sach)
        except Exception as err:
            nd.yeu_cau_sua_thong_tin = None
            raise LoiLuuTruError(f"Không lưu được yêu cầu sửa thông tin: {err}", loi_goc=err)
        self._nguoi_dung_hien_tai.yeu_cau_sua_thong_tin = yc
        bo_luu_tru.ghi_nhat_ky({
            "hanh_dong": "yeu_cau_sua_thong_tin",
            "ten_dang_nhap": nd.ten_dang_nhap,
            "chi_tiet": f"{ho_ten_s} | {email_s}",
        })
        return yc

    def lay_danh_sach_yeu_cau_sua_thong_tin(self, bo_luu_tru):
        """Admin lấy danh sách tài khoản đang có yêu cầu sửa thông tin chờ duyệt."""
        if self._nguoi_dung_hien_tai is None or self._nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ quản trị viên mới được xem yêu cầu sửa thông tin")
        return [tv for tv in bo_luu_tru.doc_danh_sach_thanh_vien() if tv.yeu_cau_sua_thong_tin]

    def duyet_sua_thong_tin(self, bo_luu_tru, ten_dang_nhap: str, chap_nhan: bool = True, ly_do: str = ""):
        """Admin duyệt (áp dụng) hoặc từ chối (kèm lý do) yêu cầu sửa thông tin."""
        if self._nguoi_dung_hien_tai is None or self._nguoi_dung_hien_tai.vai_tro != "quan_tri":
            raise KhongCoQuyenError("Chỉ quản trị viên mới được duyệt yêu cầu sửa thông tin")
        danh_sach = bo_luu_tru.doc_danh_sach_thanh_vien()
        nd = next((tv for tv in danh_sach if tv.ten_dang_nhap == ten_dang_nhap), None)
        if nd is None or not nd.yeu_cau_sua_thong_tin:
            raise DuLieuKhongHopLeError(f"Tài khoản '{ten_dang_nhap}' không có yêu cầu sửa thông tin đang chờ")
        if not chap_nhan and not (ly_do or "").strip():
            raise DuLieuKhongHopLeError("Cần nhập lý do khi từ chối yêu cầu sửa thông tin")
        yc = nd.yeu_cau_sua_thong_tin
        cu_ten, cu_email, cu_ly_do = nd.ho_ten, nd.email, nd.ly_do_tu_choi_sua
        if chap_nhan:
            ho_ten_s, email_s = self._kiem_tra_ho_ten_email(yc.get("ho_ten", ""), yc.get("email", ""), danh_sach, nd.ten_dang_nhap)
            nd.ho_ten, nd.email = ho_ten_s, email_s
            nd.ly_do_tu_choi_sua = ""
        else:
            nd.ly_do_tu_choi_sua = ly_do.strip()
        nd.yeu_cau_sua_thong_tin = None
        try:
            bo_luu_tru.ghi_danh_sach_thanh_vien(danh_sach)
        except Exception as err:
            nd.ho_ten, nd.email, nd.yeu_cau_sua_thong_tin, nd.ly_do_tu_choi_sua = cu_ten, cu_email, yc, cu_ly_do
            raise LoiLuuTruError(f"Không lưu được kết quả duyệt thông tin: {err}", loi_goc=err)
        bo_luu_tru.ghi_nhat_ky({
            "hanh_dong": "duyet_sua_thong_tin" if chap_nhan else "tu_choi_sua_thong_tin",
            "ten_dang_nhap": self._nguoi_dung_hien_tai.ten_dang_nhap,
            "thanh_vien": nd.ten_dang_nhap,
            "chi_tiet": f"{nd.ho_ten} | {nd.email}" if chap_nhan else nd.ly_do_tu_choi_sua,
        })
        return nd
