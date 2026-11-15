"""Thống kê thuần dữ liệu cho dự án Kanban; không phụ thuộc giao diện."""

from datetime import date, datetime


def thong_ke_du_an(du_an, hom_nay=None):
    """Trả về số công việc theo trạng thái, người phụ trách và hạn xử lý."""
    hom_nay = hom_nay or date.today()
    theo_trang_thai = {cot: 0 for cot in du_an.danh_sach_cot}
    theo_thanh_vien = {}
    qua_han = 0

    for cong_viec in du_an.cong_viec:
        trang_thai = cong_viec.trang_thai
        theo_trang_thai[trang_thai] = theo_trang_thai.get(trang_thai, 0) + 1
        nguoi = cong_viec.nguoi_phu_trach
        theo_thanh_vien[nguoi] = theo_thanh_vien.get(nguoi, 0) + 1
        if trang_thai != "Hoàn thành":
            han = datetime.strptime(cong_viec.ngay_ket_thuc, "%Y-%m-%d").date()
            qua_han += han < hom_nay

    tong = len(du_an.cong_viec)
    hoan_thanh = theo_trang_thai.get("Hoàn thành", 0)
    return {
        "tong": tong,
        "hoan_thanh": hoan_thanh,
        "qua_han": qua_han,
        "ty_le_hoan_thanh": round(hoan_thanh / tong * 100, 1) if tong else 0.0,
        "theo_trang_thai": theo_trang_thai,
        "theo_thanh_vien": theo_thanh_vien,
    }
