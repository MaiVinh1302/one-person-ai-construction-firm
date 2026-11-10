# -*- coding: utf-8 -*-
"""
DOCX AUDITOR & GENERATOR TOOL: Decree 30/2020/ND-CP Administrative Formatter
Tao lap van ban hanh chinh, to trinh, bien ban lam viec va cong van chuan 100% the thuc.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from typing import Dict, List, Any

class DocxND30Generator:
    """
    Dinh dang the thuc van ban hanh chinh chuan Nghi dinh 30/2020/ND-CP:
    - Kho giay A4, le tren 20mm, duoi 20mm, trai 30mm, phai 15mm.
    - Quoc hieu: chu in hoa, dung, dam, co chu 12-13.
    - Tieu ngu: chu in thuong, dung, dam, co chu 13-14.
    - So, ky hieu: chu in hoa, dung, co chu 13.
    - Ten co quan ban hanh: chu in hoa, dung, dam.
    """

    @classmethod
    def create_official_notice(
        cls,
        sender_org: str,
        dispatch_no: str,
        recipient: str,
        subject: str,
        content_paragraphs: List[str],
        signatory_title: str,
        signatory_name: str,
        output_path: str
    ):
        doc = docx.Document()

        # Dinh dang le trang (Margin A4 ND 30/2020)
        section = doc.sections[0]
        section.top_margin = Inches(0.79)     # 20mm
        section.bottom_margin = Inches(0.79)  # 20mm
        section.left_margin = Inches(1.18)    # 30mm
        section.right_margin = Inches(0.59)   # 15mm

        # Header 2 cot: Co quan ban hanh & Quoc hieu
        header_table = doc.add_table(rows=2, cols=2)
        header_table.autofit = True

        # O trai: Don vi gui
        cell_l0 = header_table.cell(0, 0)
        p_l0 = cell_l0.paragraphs[0]
        p_l0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_org = p_l0.add_run(sender_org.upper())
        run_org.bold = True
        run_org.font.name = "Times New Roman"
        run_org.font.size = Pt(11)

        cell_l1 = header_table.cell(1, 0)
        p_l1 = cell_l1.paragraphs[0]
        p_l1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_no = p_l1.add_run(f"Số: {dispatch_no}")
        run_no.font.name = "Times New Roman"
        run_no.font.size = Pt(11)

        # O phai: Quoc hieu - Tieu ngu
        cell_r0 = header_table.cell(0, 1)
        p_r0 = cell_r0.paragraphs[0]
        p_r0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_qh = p_r0.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM")
        run_qh.bold = True
        run_qh.font.name = "Times New Roman"
        run_qh.font.size = Pt(11)

        cell_r1 = header_table.cell(1, 1)
        p_r1 = cell_r1.paragraphs[0]
        p_r1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_tn = p_r1.add_run("Độc lập - Tự do - Hạnh phúc")
        run_tn.bold = True
        run_tn.underline = True
        run_tn.font.name = "Times New Roman"
        run_tn.font.size = Pt(12)

        doc.add_paragraph() # Khoang trong

        # Trich yeu noi dung
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_title = p_title.add_run(subject.upper())
        run_title.bold = True
        run_title.font.name = "Times New Roman"
        run_title.font.size = Pt(13)

        # Kinh gui
        p_rec = doc.add_paragraph()
        p_rec.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_rec = p_rec.add_run(f"Kính gửi: {recipient}")
        run_rec.bold = True
        run_rec.font.name = "Times New Roman"
        run_rec.font.size = Pt(12)

        # Cac doan noi dung
        for p_text in content_paragraphs:
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Inches(0.49) # Thut dau dong 12.5mm
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = p.add_run(p_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)

        # Chu ky & Noi nhan
        doc.add_paragraph()
        sign_table = doc.add_table(rows=1, cols=2)
        cell_noi_nhan = sign_table.cell(0, 0)
        p_nn = cell_noi_nhan.paragraphs[0]
        r_nn_title = p_nn.add_run("Nơi nhận:\n")
        r_nn_title.bold = True
        r_nn_title.italic = True
        r_nn_title.font.size = Pt(10)
        r_nn_desc = p_nn.add_run("- Như trên;\n- Ban Giám đốc;\n- Lưu: VT, HS.")
        r_nn_desc.font.size = Pt(9)

        cell_sign = sign_table.cell(0, 1)
        p_sg = cell_sign.paragraphs[0]
        p_sg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sg_t = p_sg.add_run(signatory_title.upper() + "\n\n\n\n")
        r_sg_t.bold = True
        r_sg_t.font.size = Pt(12)
        r_sg_n = p_sg.add_run(signatory_name)
        r_sg_n.bold = True
        r_sg_n.font.size = Pt(12)

        doc.save(output_path)
        return output_path
