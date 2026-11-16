"""Nhập công việc mẫu từ API công khai (DummyJSON Todos) vào dự án Kanban.

Luồng xử lý: gọi API -> kiểm tra/làm sạch -> lưu JSON (data/api_todos.json) -> tạo công việc.
Nguồn dữ liệu: https://dummyjson.com/docs/todos (miễn phí, không cần khóa API).
"""
import random
import re
from datetime import date, datetime, timedelta

from config import NHAN_HOP_LE, SO_VIEC_API_TOI_DA, TEN_FILE_API, TIMEOUT_API, URL_API_TODOS
from exceptions import KanbanException
from logger import logger
from services.quote_api import lay_du_lieu_api

MUC_UU_TIEN_NGAU_NHIEN = ("Thấp", "Trung bình", "Cao")  # "Khẩn" là loại công việc riêng nên không random
DO_DAI_TIEU_DE_TOI_DA = 80


def lam_sach_todos(du_lieu, so_luong_toi_da=SO_VIEC_API_TOI_DA):
    """Kiểm tra cấu trúc JSON của API; bỏ bản ghi thiếu/sai/trùng. Trả về list dict đã chuẩn hóa.

    Ném ValueError nếu dữ liệu không đúng dạng {"todos": [...]}.
    """
    if not isinstance(du_lieu, dict) or not isinstance(du_lieu.get("todos"), list):
        raise ValueError("Dữ liệu API sai cấu trúc: thiếu danh sách 'todos'.")

    ket_qua, da_thay = [], set()
    for muc in du_lieu["todos"]:
        if not isinstance(muc, dict):
            continue
        ma, noi_dung = muc.get("id"), muc.get("todo")
        if not isinstance(ma, int) or isinstance(ma, bool) or ma in da_thay:
            continue                                   # thiếu id, id sai kiểu hoặc trùng
        if not isinstance(noi_dung, str) or not noi_dung.strip():
            continue                                   # thiếu nội dung
        da_thay.add(ma)
        user_id = muc.get("userId")
        ket_qua.append({
            "id": ma,
            "tieu_de": " ".join(noi_dung.split())[:DO_DAI_TIEU_DE_TOI_DA],   # bỏ khoảng trắng thừa, cắt ngắn
            "hoan_thanh": muc.get("completed") is True,
            "user_id": user_id if isinstance(user_id, int) else None,
        })
        if len(ket_qua) >= so_luong_toi_da:
            break
    return ket_qua


def lay_todos_tu_api(so_luong, bo_luu_tru, skip=None):
    """Gọi API, làm sạch và lưu vào JSON. Trả về (danh_sach_sach, thong_bao_loi)."""
    if skip is None:
        skip = random.randint(0, 100)       # lấy ngẫu nhiên một đoạn trong kho dữ liệu của API
    url = f"{URL_API_TODOS}?limit={so_luong}&skip={skip}"

    du_lieu, loi = lay_du_lieu_api(url, TIMEOUT_API)
    if loi:
        return [], f"Không kết nối được API: {loi}"
    try:
        sach = lam_sach_todos(du_lieu, so_luong)
    except ValueError as err:
        return [], str(err)
    if not sach:
        return [], "API không trả về công việc hợp lệ nào."

    ban_luu = {
        "nguon": URL_API_TODOS,
        "thoi_diem": datetime.now().isoformat(timespec="seconds"),
        "todos": sach,
    }
    try:
        bo_luu_tru.ghi_json(TEN_FILE_API, ban_luu)
    except KanbanException as err:
        return [], f"Lấy được dữ liệu nhưng không lưu được file JSON: {err.thong_diep}"
    return sach, None


def _sinh_ma(du_an):
    """Sinh mã CV-xxx tiếp theo trong dự án."""
    so = [int(m.group(1)) for cv in du_an.cong_viec if (m := re.fullmatch(r"CV-(\d+)", str(cv.ma_cong_viec)))]
    return f"CV-{(max(so) + 1 if so else 1):03d}"


def nhap_cong_viec_tu_api(ql, du_an, so_luong):
    """Nhập công việc từ API vào dự án qua QuanLyKanban (có kiểm tra quyền, validation, rollback).

    Trả về dict: them / trung / loi (số lượng) và thong_bao (None nếu thành công).
    """
    ket_qua = {"them": 0, "trung": 0, "loi": 0, "thong_bao": None}
    danh_sach, loi = lay_todos_tu_api(so_luong, ql.bo_luu_tru)
    if loi:
        ket_qua["thong_bao"] = loi
        return ket_qua

    nguoi = ql.nguoi_dung_hien_tai.ten_dang_nhap
    hom_nay = date.today()
    for todo in danh_sach:
        the_nguon = f"[API#{todo['id']}]"          # đánh dấu để lần sau không nhập trùng
        if any(the_nguon in (cv.mo_ta or "") for cv in du_an.cong_viec):
            ket_qua["trung"] += 1
            continue
        du_lieu = {
            "ma_cong_viec": _sinh_ma(du_an),
            "tieu_de": todo["tieu_de"],
            "mo_ta": f"Nhập từ DummyJSON API {the_nguon}",
            "nguoi_phu_trach": nguoi,
            "ngay_bat_dau": hom_nay.isoformat(),
            "ngay_ket_thuc": (hom_nay + timedelta(days=random.randint(3, 14))).isoformat(),
            "trang_thai": "Hoàn thành" if todo["hoan_thanh"] else "Cần làm",
            "muc_uu_tien": random.choice(MUC_UU_TIEN_NGAU_NHIEN),
            "nhan": random.choice(NHAN_HOP_LE),
        }
        try:
            ql.tao_cong_viec(du_an, du_lieu)
            ket_qua["them"] += 1
        except KanbanException as err:
            ket_qua["loi"] += 1
            logger.warning(f"Bỏ qua việc API #{todo['id']}: {err.thong_diep}")
    return ket_qua