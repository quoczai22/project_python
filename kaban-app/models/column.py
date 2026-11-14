"""models.column: Đối tượng Column đại diện cho một cột trạng thái trên bảng Kanban."""
from typing import List, Optional
from models.CongViec.CongViecBase import CongViec


class Column:
    """
    Đại diện cho 1 cột trạng thái Kanban:
    - ten_cot: Tên cột (Cần làm, Đang làm, Kiểm tra, Hoàn thành)
    - gioi_han_wip: Giới hạn số lượng công việc cùng lúc (Work In Progress)
    - danh_sach_cong_viec: Danh sách các đối tượng CongViec / Task thuộc cột
    """

    def __init__(self, ten_cot: str, gioi_han_wip: int = 0):
        self.ten_cot = ten_cot
        self.gioi_han_wip = gioi_han_wip
        self.danh_sach_cong_viec: List[CongViec] = []

    def them_cong_viec(self, cv: CongViec):
        self.danh_sach_cong_viec.append(cv)

    def xoa_cong_viec(self, ma_cong_viec: str) -> Optional[CongViec]:
        for i, cv in enumerate(self.danh_sach_cong_viec):
            if cv.ma_cong_viec == ma_cong_viec:
                return self.danh_sach_cong_viec.pop(i)
        return None

    def so_luong(self) -> int:
        return len(self.danh_sach_cong_viec)

    def qua_wip(self) -> bool:
        return self.gioi_han_wip > 0 and self.so_luong() > self.gioi_han_wip

    def to_dict(self) -> dict:
        return {
            "ten_cot": self.ten_cot,
            "gioi_han_wip": self.gioi_han_wip,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Column":
        return cls(
            ten_cot=data.get("ten_cot", ""),
            gioi_han_wip=data.get("gioi_han_wip", 0),
        )
