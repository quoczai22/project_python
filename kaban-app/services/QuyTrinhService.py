"""Các thao tác duyệt, gia hạn và xóa mềm, dùng chung cho UI và facade."""
from datetime import date, datetime

from exceptions import DuLieuKhongHopLeError, KhongCoQuyenError, KhongTimThayError, LoiLuuTruError


class QuyTrinhService:
    def __init__(self, du_an_service, xac_thuc, bo_luu_tru):
        self.du_an_service = du_an_service
        self.xac_thuc = xac_thuc
        self.bo_luu_tru = bo_luu_tru

    def _nguoi(self):
        nd = self.xac_thuc.nguoi_dung_hien_tai
        if nd is None:
            raise KhongCoQuyenError("Bạn chưa đăng nhập")
        return nd

    def _viec(self, du_an, ma_cong_viec):
        cv = du_an.tim_cong_viec_theo_ma(ma_cong_viec)
        if cv is None:
            raise KhongTimThayError(f"Không tìm thấy công việc {ma_cong_viec}")
        return cv

    def _duyet_duoc(self, du_an, cv, nguoi_yeu_cau=None):
        nd = self._nguoi()
        if nd.vai_tro == "quan_tri":
            return True
        nguoi = nguoi_yeu_cau or cv.nguoi_tao
        return (nd.vai_tro == "truong_nhom" and
                nguoi != nd.ten_dang_nhap and
                nguoi in du_an.nhom.get(nd.ten_dang_nhap, []))

    def _luu(self, du_an, cv, snapshot, hanh_dong, chi_tiet=None):
        try:
            self.du_an_service.luu_du_lieu()
        except Exception as err:
            from models.CongViec import CongViec
            phuc_hoi = CongViec.from_dict(snapshot)
            cv.__dict__.clear()
            cv.__dict__.update(phuc_hoi.__dict__)
            raise LoiLuuTruError(f"Không lưu được {hanh_dong}: {err}", loi_goc=err)
        self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": hanh_dong,
            "ma_du_an": du_an.ma_du_an, "ma_cong_viec": cv.ma_cong_viec,
            "ten_dang_nhap": self._nguoi().ten_dang_nhap, "chi_tiet": chi_tiet or ""})
        return cv

    def duyet_cong_viec(self, du_an, ma_cong_viec, chap_nhan=True):
        cv = self._viec(du_an, ma_cong_viec)
        if cv.trang_thai_duyet != "cho_duyet" or not self._duyet_duoc(du_an, cv):
            raise KhongCoQuyenError("Không có quyền duyệt công việc này")
        old = cv.to_dict()
        cv.trang_thai_duyet = "da_duyet" if chap_nhan else "tu_choi"
        return self._luu(du_an, cv, old, "duyet_cong_viec", cv.trang_thai_duyet)

    def gui_lai_cong_viec(self, du_an, ma_cong_viec):
        cv = self._viec(du_an, ma_cong_viec)
        if cv.trang_thai_duyet != "tu_choi" or self._nguoi().ten_dang_nhap != cv.nguoi_tao:
            raise KhongCoQuyenError("Chỉ người tạo được gửi lại việc bị từ chối")
        old = cv.to_dict()
        cv.trang_thai_duyet = "cho_duyet"
        return self._luu(du_an, cv, old, "gui_lai_cong_viec")

    def yeu_cau_mo_lai(self, du_an, ma_cong_viec, ly_do):
        cv = self._viec(du_an, ma_cong_viec)
        nd = self._nguoi()
        if cv.trang_thai != "Hoàn thành" or nd.ten_dang_nhap != cv.nguoi_phu_trach or not ly_do.strip():
            raise DuLieuKhongHopLeError("Chỉ người phụ trách được xin mở lại việc hoàn thành, kèm lý do")
        if cv.yeu_cau_mo_lai:
            raise DuLieuKhongHopLeError("Yêu cầu mở lại đang chờ duyệt")
        old = cv.to_dict()
        cv.yeu_cau_mo_lai = {"nguoi": nd.ten_dang_nhap, "ly_do": ly_do.strip()}
        return self._luu(du_an, cv, old, "yeu_cau_mo_lai", ly_do)

    def duyet_mo_lai(self, du_an, ma_cong_viec, chap_nhan=True):
        cv = self._viec(du_an, ma_cong_viec)
        if not cv.yeu_cau_mo_lai or not self._duyet_duoc(du_an, cv, cv.yeu_cau_mo_lai["nguoi"]):
            raise KhongCoQuyenError("Không có yêu cầu hoặc không có quyền duyệt")
        old = cv.to_dict()
        if chap_nhan:
            cv.trang_thai = "Cần làm"
        cv.yeu_cau_mo_lai = None
        return self._luu(du_an, cv, old, "mo_lai" if chap_nhan else "tu_choi_mo_lai")

    def yeu_cau_gia_han(self, du_an, ma_cong_viec, han_moi, ly_do):
        cv = self._viec(du_an, ma_cong_viec)
        nd = self._nguoi()
        try:
            ngay = date.fromisoformat(han_moi)
        except (TypeError, ValueError):
            raise DuLieuKhongHopLeError("Hạn mới phải có dạng YYYY-MM-DD")
        if (nd.ten_dang_nhap != cv.nguoi_phu_trach or not cv.da_qua_han() or
                ngay <= date.today() or not ly_do.strip() or len(cv.lich_su_gia_han) >= 3):
            raise DuLieuKhongHopLeError("Gia hạn yêu cầu việc quá hạn, ngày tương lai, lý do và tối đa 3 lần")
        if cv.yeu_cau_gia_han:
            raise DuLieuKhongHopLeError("Yêu cầu gia hạn đang chờ duyệt")
        old = cv.to_dict()
        cv.yeu_cau_gia_han = {"han_moi": han_moi, "ly_do": ly_do.strip(), "nguoi": nd.ten_dang_nhap}
        return self._luu(du_an, cv, old, "yeu_cau_gia_han", han_moi)

    def duyet_gia_han(self, du_an, ma_cong_viec, chap_nhan=True):
        cv = self._viec(du_an, ma_cong_viec)
        if not cv.yeu_cau_gia_han or not self._duyet_duoc(du_an, cv, cv.yeu_cau_gia_han["nguoi"]):
            raise KhongCoQuyenError("Không có yêu cầu hoặc không có quyền duyệt")
        old = cv.to_dict()
        yeu_cau = cv.yeu_cau_gia_han
        if not chap_nhan:
            cv.yeu_cau_gia_han = None
            return self._luu(du_an, cv, old, "tu_choi_gia_han", yeu_cau["han_moi"])
        if date.fromisoformat(yeu_cau["han_moi"]) <= date.today():
            raise DuLieuKhongHopLeError("Hạn mới đã qua, cần gửi lại yêu cầu")
        cv.ngay_ket_thuc = yeu_cau["han_moi"]
        cv.lich_su_gia_han.append({**yeu_cau, "han_cu": old["NgayKetThuc"]})
        cv.yeu_cau_gia_han = None
        return self._luu(du_an, cv, old, "gia_han", cv.ngay_ket_thuc)

    def huy_cong_viec(self, du_an, ma_cong_viec, ly_do):
        cv = self._viec(du_an, ma_cong_viec)
        nd = self._nguoi()
        if (nd.vai_tro != "quan_tri" and not
                (nd.vai_tro == "truong_nhom" and cv.nguoi_phu_trach in du_an.nhom.get(nd.ten_dang_nhap, []))):
            raise KhongCoQuyenError("Không có quyền hủy công việc này")
        if cv.trang_thai == "Đã hủy" or not ly_do.strip():
            raise DuLieuKhongHopLeError("Việc đã hủy hoặc thiếu lý do hủy")
        old = cv.to_dict()
        cv.trang_thai_truoc_huy = cv.trang_thai
        cv.trang_thai = "Đã hủy"
        cv.ly_do_huy, cv.nguoi_huy = ly_do.strip(), nd.ten_dang_nhap
        cv.thoi_gian_huy = datetime.now().isoformat()
        return self._luu(du_an, cv, old, "huy_cong_viec", ly_do)

    def khoi_phuc_cong_viec(self, du_an, ma_cong_viec):
        cv = self._viec(du_an, ma_cong_viec)
        nd = self._nguoi()
        if cv.trang_thai != "Đã hủy" or (nd.vai_tro != "quan_tri" and not
                (nd.vai_tro == "truong_nhom" and cv.nguoi_phu_trach in du_an.nhom.get(nd.ten_dang_nhap, []))):
            raise KhongCoQuyenError("Không có quyền khôi phục công việc này")
        old = cv.to_dict()
        cv.trang_thai = cv.trang_thai_truoc_huy or "Cần làm"
        cv.ly_do_huy = cv.nguoi_huy = cv.thoi_gian_huy = cv.trang_thai_truoc_huy = ""
        return self._luu(du_an, cv, old, "khoi_phuc_cong_viec")
