# -*- coding: utf-8 -*-
"""
KNOWLEDGE ENGINE: Central Construction Legal Library 2026 Connector
Ket noi truc tiep vao Thu vien Phap luat Xay dung 2026:
D:\\OneDrive - CONG TY CO PHAN TAP DOAN T&T\\VINH\\THU_VIEN_PHAP_LUAT_XAY_DUNG_2026
"""

import os
import sys
import openpyxl

LEGAL_DIR = r"D:\OneDrive - CONG TY CO PHAN TAP DOAN T&T\VINH\THU_VIEN_PHAP_LUAT_XAY_DUNG_2026"
EXCEL_PATH = os.path.join(LEGAL_DIR, "BANG_TRA_CUU_PHAP_LUAT_XAY_DUNG_2026.xlsx")
TEXT_FULL_PATH = os.path.join(LEGAL_DIR, "CAC_NGHI_DINH_XAY_DUNG_MOI_2026_FULL.txt")

# Core Ground-Truth Regulations for 2026
CORE_REGULATIONS = {
    "CONTRACTS": {
        "primary": "Nghị định 210/2026/NĐ-CP (Hiệu lực 01/07/2026)",
        "transition": "Nghị định 37/2015/NĐ-CP & Nghị định 50/2021/NĐ-CP (Hợp đồng ký trước 01/07/2026)",
        "template": "Thông tư 02/2023/TT-BXD (Mẫu hợp đồng thi công & điều chỉnh đơn giá)",
        "rules": [
            "Tạm ứng hợp đồng không vượt quá 30% giá hợp đồng (Khoản 2 Điều 18 NĐ 210/2026/NĐ-CP).",
            "Mức tạm ứng trên 01 tỷ đồng bắt buộc phải nộp Bảo lãnh tiền tạm ứng của ngân hàng.",
            "Thời hạn quyết toán hợp đồng tối đa 60 ngày kể từ ngày nghiệm thu bàn giao (công trình quy mô lớn tối đa 120 ngày).",
            "Thanh toán theo mốc hoàn thành không bắt buộc phải ký phụ lục hợp đồng bổ sung mỗi đợt."
        ]
    },
    "BIDDING": {
        "primary": "Luật Đấu thầu số 22/2023/QH15 & Văn bản hợp nhất 74/VBHN-VPQH (2026)",
        "procurement": "Nghị định 349/2026/NĐ-CP (Hiệu lực 09/09/2026)",
        "prior": "Nghị định 24/2024/NĐ-CP & Thông tư 06/2024/TT-BKHĐT",
        "rules": [
            "Hạn mức chỉ định thầu xây lắp nâng lên tối đa 05 tỷ đồng (NĐ 349/2026/NĐ-CP).",
            "Hạn mức chỉ định thầu dịch vụ tư vấn nâng lên tối đa 03 tỷ đồng (NĐ 349/2026/NĐ-CP).",
            "Loại trừ báo giá chênh lệch trên 30% so với giá trung bình khi xác định giá gói thầu.",
            "Bắt buộc đăng tải công khai yêu cầu báo giá trên Hệ thống Mạng Đấu thầu Quốc gia."
        ]
    },
    "QAQC": {
        "primary": "Nghị định 06/2021/NĐ-CP & Nghị định 35/2023/NĐ-CP",
        "inspection": "Thông tư 10/2021/TT-BXD (Nhật ký công trình & Biên bản nghiệm thu công việc BBNTCV)",
        "rules": [
            "Mẫu dấu bản vẽ hoàn công bắt buộc tuân thủ Phụ lục II Nghị định 06/2021/NĐ-CP (Đủ 4 chữ ký: TVGS, TVTK, Chỉ huy trưởng, Đại diện CĐT).",
            "Nghiệm thu chuyển bước thi công phải có đầy đủ kết quả thí nghiệm vật liệu đạt chuẩn.",
            "Nhật ký thi công phải đóng dấu giáp lai, ghi chép liên tục từng ngày (nhiệt độ, nhân lực, thiết bị, sự cố phát sinh)."
        ]
    },
    "SETTLEMENT": {
        "primary": "Nghị định 99/2021/NĐ-CP (Thanh toán vốn đầu tư công)",
        "treasury": "Thông tư 96/2021/TT-BTC (Kiểm soát thanh toán qua Kho bạc)",
        "rules": [
            "Thanh toán khối lượng hoàn thành bắt buộc dùng Mẫu số 08a ban hành kèm NĐ 99/2021/NĐ-CP.",
            "Bảng xác định giá trị thu hồi tạm ứng bắt buộc dùng Mẫu số 08b kèm NĐ 99/2021/NĐ-CP.",
            "Giá trị đề nghị thanh toán lũy kế không được vượt giá trị hợp đồng hoặc dự toán được duyệt.",
            "Bắt buộc khấu trừ đầy đủ tỷ lệ thu hồi tạm ứng và bảo hành giữ lại (thường 5%)."
        ]
    },
    "COST_NORMS": {
        "primary": "Nghị định 10/2021/NĐ-CP (Tổng mức đầu tư 7 thành phần)",
        "norms": "Thông tư 09/2024/TT-BXD (Sửa đổi, bổ sung định mức xây dựng TT 12/2021/TT-BXD)",
        "unit_costs": "Quyết định 1247/QĐ-BXD (Suất vốn đầu tư xây dựng công trình)",
        "standards": "QCVN 06:2022/BXD (Sửa đổi 1:2023) về An toàn cháy & QCVN 07:2019/BXD",
        "rules": [
            "Tổng mức đầu tư gồm 7 chi phí: Bồi thường GPMB, Xây dựng, Thiết bị, QLDA, TVĐTXD, Chi phí khác, Dự phòng phí.",
            "Áp dụng định mức hao phí nhân công và máy thi công theo Thông tư 09/2024/TT-BXD mới nhất."
        ]
    }
}

class ConstructionLegalEngine:
    def __init__(self):
        self.legal_dir = LEGAL_DIR
        self.excel_path = EXCEL_PATH
        self.has_excel = os.path.exists(self.excel_path)
        self.cached_laws = []
        if self.has_excel:
            self._load_excel_cache()

    def _load_excel_cache(self):
        try:
            wb = openpyxl.load_workbook(self.excel_path, data_only=True)
            ws = wb.active
            for r in range(5, ws.max_row + 1):
                so_hieu = ws.cell(r, 3).value
                if not so_hieu:
                    continue
                self.cached_laws.append({
                    "stt": ws.cell(r, 1).value or "",
                    "linh_vuc": ws.cell(r, 2).value or "",
                    "so_hieu": str(so_hieu).strip(),
                    "ten_vb": str(ws.cell(r, 4).value or "").strip(),
                    "ngay_bh": str(ws.cell(r, 5).value or "").strip(),
                    "ngay_hl": str(ws.cell(r, 6).value or "").strip(),
                    "co_quan": str(ws.cell(r, 7).value or "").strip(),
                    "tinh_trang": str(ws.cell(r, 8).value or "").strip(),
                    "diem_moi": str(ws.cell(r, 9).value or "").strip(),
                    "tep_tin": str(ws.cell(r, 10).value or "").strip()
                })
        except Exception as e:
            print(f"[Warning] Khong the tai Excel tra cuu: {e}", file=sys.stderr)

    def search_law(self, keyword, domain=None):
        """
        Tra cuu van ban phap ly xay dung chinh xac, co doi chieu thoi diem hieu luc
        """
        kw = keyword.lower().strip()
        results = []
        for law in self.cached_laws:
            search_str = f"{law['so_hieu']} {law['ten_vb']} {law['linh_vuc']} {law['diem_moi']}".lower()
            if kw in search_str:
                if domain and domain.lower() not in law['linh_vuc'].lower():
                    continue
                results.append(law)
        return results

    def get_grounding_rules(self, domain_key):
        """
        Tra ve bo nguyen tac phap ly bat buoc 2026 cho tung phong ban chuyen mon
        """
        return CORE_REGULATIONS.get(domain_key.upper(), {})

# Global Singleton Instance
legal_engine = ConstructionLegalEngine()
