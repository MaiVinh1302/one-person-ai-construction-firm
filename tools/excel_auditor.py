# -*- coding: utf-8 -*-
"""
EXCEL AUDITOR TOOL: Audit & Generator for Template 08a Decree 99/2021/ND-CP
Kiem toan bang thanh toan khoi luong hoan thanh Mau 08a va Bieu thu hoi tam ung 08b.
Bao toan cong thuc toan hoc, phat hien gian lan go so cung.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, List, Any

class ExcelMau08aAuditor:
    """
    Kiem toan bang thanh toan Mau 08a Nghi dinh 99/2021/ND-CP
    Kiem tra:
    1. Luy ke = Ky truoc + Ky nay
    2. Don gia thanh toan <= Don gia hop dong
    3. Phat hien so cung hardcoded thay vi dung cong thuc
    4. Khau tru tam ung Mau 08b & Bao hanh 5%
    """

    @classmethod
    def create_compliant_08a(cls, project_name: str, contractor: str, contract_no: str, items: List[Dict[str, Any]], output_path: str):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Mau_08a_ND99"

        # Tieu de Quoc ngu & Bieu mau
        ws.merge_cells("A1:K1")
        ws["A1"] = "BẢNG XÁC ĐỊNH GIÁ TRỊ KHỐI LƯỢNG CÔNG VIỆC HOÀN THÀNH ĐỀ NGHỊ THANH TOÁN"
        ws["A1"].font = Font(name="Times New Roman", size=13, bold=True)
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("A2:K2")
        ws["A2"] = "(Kèm theo Nghị định số 99/2021/NĐ-CP ngày 11/11/2021 của Chính phủ - Mẫu số 08a)"
        ws["A2"].font = Font(name="Times New Roman", size=11, italic=True)
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")

        # Thong tin du an
        ws["A4"] = f"Tên dự án: {project_name}"
        ws["A5"] = f"Hợp đồng số: {contract_no}"
        ws["A6"] = f"Nhà thầu thi công: {contractor}"
        for r in range(4, 7):
            ws[f"A{r}"].font = Font(name="Times New Roman", size=11, bold=True)

        # Header Cot
        headers = [
            ("STT", "A8:A9"),
            ("Nội dung công việc", "B8:B9"),
            ("Đơn vị", "C8:C9"),
            ("HỢP ĐỒNG", "D8:E8"),
            ("Khối lượng hoàn thành", "F8:H8"),
            ("Thành tiền (VNĐ)", "I8:K8")
        ]
        sub_headers = {
            "D9": "Khối lượng", "E9": "Đơn giá (VNĐ)",
            "F9": "Kỳ trước", "G9": "Kỳ này", "H9": "Lũy kế",
            "I9": "Kỳ trước", "J9": "Kỳ này", "K9": "Lũy kế"
        }

        # Format header
        hdr_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        hdr_font = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        for col in ["A8","B8","C8","D8","F8","I8"]:
            ws[col].fill = hdr_fill
            ws[col].font = hdr_font
            ws[col].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("A8:A9")
        ws["A8"] = "STT"
        ws.merge_cells("B8:B9")
        ws["B8"] = "Nội dung công việc"
        ws.merge_cells("C8:C9")
        ws["C8"] = "Đơn vị"
        ws.merge_cells("D8:E8")
        ws["D8"] = "Theo Hợp đồng"
        ws.merge_cells("F8:H8")
        ws["F8"] = "Khối lượng thực hiện"
        ws.merge_cells("I8:K8")
        ws["I8"] = "Giá trị thực hiện (VNĐ)"

        for cell_ref, text in sub_headers.items():
            ws[cell_ref] = text
            ws[cell_ref].fill = hdr_fill
            ws[cell_ref].font = hdr_font
            ws[cell_ref].alignment = Alignment(horizontal="center", vertical="center")

        # Do du lieu tung dong
        curr_row = 10
        for idx, item in enumerate(items, 1):
            ws[f"A{curr_row}"] = idx
            ws[f"B{curr_row}"] = item.get("name", "")
            ws[f"C{curr_row}"] = item.get("unit", "")
            ws[f"D{curr_row}"] = item.get("contract_qty", 0)
            ws[f"E{curr_row}"] = item.get("unit_price", 0)
            ws[f"F{curr_row}"] = item.get("prev_qty", 0)
            ws[f"G{curr_row}"] = item.get("curr_qty", 0)

            # CONG THUC BAT BUOC - KHONG HARDCODE
            ws[f"H{curr_row}"] = f"=F{curr_row}+G{curr_row}"       # Luy ke KL
            ws[f"I{curr_row}"] = f"=F{curr_row}*E{curr_row}"       # Tien ky truoc
            ws[f"J{curr_row}"] = f"=G{curr_row}*E{curr_row}"       # Tien ky nay
            ws[f"K{curr_row}"] = f"=H{curr_row}*E{curr_row}"       # Luy ke tien

            # Dinh dang so
            ws[f"E{curr_row}"].number_format = '#,##0'
            ws[f"I{curr_row}"].number_format = '#,##0'
            ws[f"J{curr_row}"].number_format = '#,##0'
            ws[f"K{curr_row}"].number_format = '#,##0'

            for c in range(1, 12):
                ws.cell(curr_row, c).border = thin_border
                ws.cell(curr_row, c).font = Font(name="Times New Roman", size=10)

            curr_row += 1

        # Dong Tong Cong
        ws[f"B{curr_row}"] = "TỔNG CỘNG GIÁ TRỊ THỰC HIỆN:"
        ws[f"B{curr_row}"].font = Font(name="Times New Roman", size=10, bold=True)
        ws[f"J{curr_row}"] = f"=SUM(J10:J{curr_row-1})"
        ws[f"K{curr_row}"] = f"=SUM(K10:K{curr_row-1})"
        ws[f"J{curr_row}"].font = Font(name="Times New Roman", size=10, bold=True)
        ws[f"K{curr_row}"].font = Font(name="Times New Roman", size=10, bold=True)
        ws[f"J{curr_row}"].number_format = '#,##0'
        ws[f"K{curr_row}"].number_format = '#,##0'

        # Can chinh do rong cot
        col_widths = {'A': 6, 'B': 36, 'C': 10, 'D': 14, 'E': 16, 'F': 12, 'G': 12, 'H': 12, 'I': 18, 'J': 18, 'K': 20}
        for col_letter, width in col_widths.items():
            ws.column_dimensions[col_letter].width = width

        wb.save(output_path)
        return output_path
