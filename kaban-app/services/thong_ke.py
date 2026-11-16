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


def xuat_bao_cao_file(du_an, duong_dan_file: str, ql=None) -> str:
    """
    Xuất báo cáo tiến độ dự án Kanban ra file văn bản (.txt) hoặc bảng tính (.csv).
    Trả về đường dẫn file đã ghi.
    """
    tk = thong_ke_du_an(du_an)
    duoi_file = duong_dan_file.lower()

    if duoi_file.endswith(".csv"):
        import csv
        with open(duong_dan_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["BÁO CÁO TIẾN ĐỘ DỰ ÁN KANBAN"])
            writer.writerow(["Mã dự án", du_an.ma_du_an])
            writer.writerow(["Tên dự án", du_an.ten_du_an])
            writer.writerow(["Thời gian xuất", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            writer.writerow(["TỔNG QUAN"])
            writer.writerow(["Tổng số công việc", tk["tong"]])
            writer.writerow(["Đã hoàn thành", tk["hoan_thanh"]])
            writer.writerow(["Quá hạn", tk["qua_han"]])
            writer.writerow(["Tỷ lệ hoàn thành (%)", tk["ty_le_hoan_thanh"]])
            writer.writerow([])
            writer.writerow(["PHÂN BỔ THEO CỘT"])
            for cot, sl in tk["theo_trang_thai"].items():
                writer.writerow([cot, sl])
            writer.writerow([])
            writer.writerow(["DANH SÁCH CHI TIẾT CÔNG VIỆC"])
            writer.writerow(["Mã", "Tiêu đề", "Trạng thái", "Ưu tiên", "Phụ trách", "Bắt đầu", "Kết thúc", "Cảnh báo"])
            for cv in du_an.cong_viec:
                writer.writerow([
                    cv.ma_cong_viec, cv.tieu_de, cv.trang_thai,
                    cv.muc_uu_tien, cv.nguoi_phu_trach,
                    cv.ngay_bat_dau, cv.ngay_ket_thuc, cv.canh_bao()
                ])
    else:
        # Mặc định định dạng text (.txt) đẹp, rõ ràng
        ngay_xuat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "=" * 60,
            f"          BÁO CÁO TIẾN ĐỘ DỰ ÁN KANBAN",
            "=" * 60,
            f"Dự án       : {du_an.ma_du_an} - {du_an.ten_du_an}",
            f"Thời gian   : {ngay_xuat}",
            "-" * 60,
            "1. TỔNG QUAN TIẾN ĐỘ:",
            f"  • Tổng số công việc : {tk['tong']}",
            f"  • Đã hoàn thành    : {tk['hoan_thanh']}",
            f"  • Quá hạn          : {tk['qua_han']}",
            f"  • Tỷ lệ hoàn thành : {tk['ty_le_hoan_thanh']}%",
            "",
            "2. PHÂN BỔ CÔNG VIỆC THEO CỘT:",
        ]
        for cot, sl in tk["theo_trang_thai"].items():
            lines.append(f"  • {cot:<15}: {sl} việc")

        lines.extend([
            "",
            "3. PHÂN BỔ THEO THÀNH VIÊN:",
        ])
        for tv, sl in tk["theo_thanh_vien"].items():
            lines.append(f"  • {tv:<15}: {sl} việc")

        lines.extend([
            "",
            "-" * 60,
            "4. DANH SÁCH CHI TIẾT CÔNG VIỆC:",
            f"{'MÃ':<10} {'TRẠNG THÁI':<14} {'ƯU TIÊN':<12} {'PHỤ TRÁCH':<12} {'HẠN CHÓT':<12} {'TIÊU ĐỀ'}",
            "-" * 60,
        ])
        for cv in du_an.cong_viec:
            lines.append(
                f"{cv.ma_cong_viec:<10} {cv.trang_thai:<14} {cv.muc_uu_tien:<12} {cv.nguoi_phu_trach:<12} {cv.ngay_ket_thuc:<12} {cv.tieu_de}"
            )
            if cv.can_chu_y():
                lines.append(f"   ↳ [Cảnh báo]: {cv.canh_bao()}")

        lines.append("=" * 60)
        with open(duong_dan_file, mode="w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return duong_dan_file
