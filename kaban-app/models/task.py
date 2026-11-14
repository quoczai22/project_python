"""models.task: Re-export và alias lớp đối tượng công việc Task."""
from models.CongViec.CongViecBase import CongViec
from models.CongViec.CongViecThuong import CongViecThuong
from models.CongViec.CongViecKhan import CongViecKhan

# Alias tương thích kiến trúc chuẩn
Task = CongViecThuong
UrgentTask = CongViecKhan

__all__ = [
    "CongViec",
    "CongViecThuong",
    "CongViecKhan",
    "Task",
    "UrgentTask",
]
