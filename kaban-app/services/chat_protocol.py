"""Giao thức tin nhắn bình luận thời gian thực (WebSocket) dùng chung cho server và client.

Mỗi tin là một đối tượng JSON có khóa "loai":
    vao_phong      client -> server  {"loai", "phong", "nguoi"}
    roi_phong      client -> server  {"loai", "phong"}
    binh_luan      hai chiều         {"loai", "phong", "binh_luan": BinhLuan.to_dict()}
    xoa_binh_luan  hai chiều         {"loai", "phong", "ma_binh_luan", "nguoi"}
    lich_su        server -> client  {"loai", "phong", "danh_sach": [BinhLuan.to_dict(), ...]}
    loi            server -> client  {"loai", "thong_diep"}

Phòng = một công việc, khóa "<MaDuAn>/<MaCongViec>", ví dụ "DA-001/CV-003".
"""
import json
import re

from models.BinhLuan import BinhLuan

DO_DAI_BINH_LUAN_TOI_DA = 500
KICH_THUOC_TIN_TOI_DA = 64 * 1024   # byte, server từ chối khung lớn hơn

LOAI_HOP_LE = {"vao_phong", "roi_phong", "binh_luan", "xoa_binh_luan", "lich_su", "loi"}
_MAU_PHONG = re.compile(r"[A-Za-z0-9_-]{1,32}/[A-Za-z0-9_-]{1,32}")
_MAU_TEN = re.compile(r"[A-Za-z0-9_]{1,32}")


def tao_phong(ma_du_an: str, ma_cong_viec: str) -> str:
    phong = f"{ma_du_an}/{ma_cong_viec}"
    if not _MAU_PHONG.fullmatch(phong):
        raise ValueError(f"Mã phòng không hợp lệ: {phong!r}")
    return phong


def tach_phong(phong: str):
    """Trả về (ma_du_an, ma_cong_viec)."""
    ma_du_an, ma_cong_viec = phong.split("/", 1)
    return ma_du_an, ma_cong_viec


def dong_goi(tin: dict) -> str:
    return json.dumps(tin, ensure_ascii=False)


def _kiem_tra_binh_luan(du_lieu) -> dict:
    if not isinstance(du_lieu, dict):
        raise ValueError("'binh_luan' phải là đối tượng")
    try:
        bl = BinhLuan.from_dict(du_lieu)
    except Exception as loi:   # DuLieuKhongHopLeError hoặc kiểu dữ liệu sai
        raise ValueError(f"Bình luận không hợp lệ: {loi}") from loi
    if len(bl.noi_dung) > DO_DAI_BINH_LUAN_TOI_DA:
        raise ValueError(f"Bình luận vượt quá {DO_DAI_BINH_LUAN_TOI_DA} ký tự")
    return bl.to_dict()


def giai_ma(tho) -> dict:
    """Đọc và kiểm tra một tin nhận được; ném ValueError nếu sai giao thức."""
    if isinstance(tho, bytes):
        tho = tho.decode("utf-8")
    try:
        tin = json.loads(tho)
    except (TypeError, ValueError) as loi:
        raise ValueError("Tin nhắn không phải JSON hợp lệ") from loi
    if not isinstance(tin, dict) or tin.get("loai") not in LOAI_HOP_LE:
        raise ValueError("Thiếu hoặc sai trường 'loai'")

    loai = tin["loai"]
    if loai == "loi":
        return {"loai": "loi", "thong_diep": str(tin.get("thong_diep", ""))}

    phong = tin.get("phong")
    if not isinstance(phong, str) or not _MAU_PHONG.fullmatch(phong):
        raise ValueError("Thiếu hoặc sai trường 'phong'")
    sach = {"loai": loai, "phong": phong}

    if loai == "vao_phong":
        nguoi = tin.get("nguoi")
        if not isinstance(nguoi, str) or not _MAU_TEN.fullmatch(nguoi):
            raise ValueError("Thiếu hoặc sai trường 'nguoi'")
        sach["nguoi"] = nguoi
    elif loai == "binh_luan":
        sach["binh_luan"] = _kiem_tra_binh_luan(tin.get("binh_luan"))
    elif loai == "xoa_binh_luan":
        ma = tin.get("ma_binh_luan")
        if not isinstance(ma, str) or not ma.strip() or len(ma) > 64:
            raise ValueError("Thiếu hoặc sai trường 'ma_binh_luan'")
        sach["ma_binh_luan"] = ma.strip()
        nguoi = tin.get("nguoi")
        if isinstance(nguoi, str) and _MAU_TEN.fullmatch(nguoi):
            sach["nguoi"] = nguoi
    elif loai == "lich_su":
        ds = tin.get("danh_sach")
        if not isinstance(ds, list):
            raise ValueError("'danh_sach' phải là danh sách")
        sach["danh_sach"] = [_kiem_tra_binh_luan(muc) for muc in ds]
    return sach
