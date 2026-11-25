"""Sắp xếp thẻ Kanban và khôi phục thứ tự nếu lưu thất bại."""

from exceptions import LoiLuuTruError


def chen_cong_viec(du_an, cong_viec, cot, vi_tri, luu_du_lieu, cung_cot=False):
    danh_sach = du_an.danh_sach_cong_viec
    thu_tu_cu = danh_sach[:]

    if cung_cot:
        vi_tri_cu = [cv for cv in danh_sach if cv.trang_thai == cot].index(cong_viec)
        if vi_tri is not None and vi_tri_cu < vi_tri:
            vi_tri -= 1

    danh_sach.remove(cong_viec)
    trong_cot = [cv for cv in danh_sach if cv.trang_thai == cot]
    if vi_tri is not None and 0 <= vi_tri < len(trong_cot):
        danh_sach.insert(danh_sach.index(trong_cot[vi_tri]), cong_viec)
    else:
        danh_sach.append(cong_viec)

    try:
        luu_du_lieu()
    except Exception as loi:
        danh_sach[:] = thu_tu_cu
        raise LoiLuuTruError("Không thể lưu thứ tự công việc", loi_goc=loi) from loi
