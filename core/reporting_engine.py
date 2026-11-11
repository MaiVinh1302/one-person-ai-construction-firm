# -*- coding: utf-8 -*-
"""
REPORTING ENGINE: Construction Enterprise Executive & Departmental Reporting System
Chuyên trách xuất bản:
1. BỘ BÁO CÁO TỔNG THỂ CÔNG TY (Master Executive Dossier) kèm đầy đủ báo cáo 5 phòng ban.
2. BÁO CÁO THẨM TRA RIÊNG BIỆT TỪNG PHÒNG BAN (Standalone Departmental Audit Report) khi chỉ thực hiện 1 quy trình.
3. BÁO CÁO TỔNG HỢP CHUYÊN ĐỀ THEO YÊU CẦU (Modular Multi-Workflow Report) khi thực hiện kết hợp 2-4 quy trình tùy chọn.
Chuẩn hóa thể thức hành chính theo Nghị định 30/2020/NĐ-CP và trích dẫn chuẩn Pháp luật Xây dựng 2026.
"""

import os
import datetime
from typing import Dict, List, Any, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class ConstructionReportingEngine:
    """
    Hệ thống sinh báo cáo đa tầng cho Công ty Xây dựng 1 Người:
    - Trình bày trực quan, trang trọng, số liệu truy vết minh bạch.
    - Hỗ trợ xuất Markdown và xuất file Word .docx tiêu chuẩn.
    """

    COMPANY_NAME = "T&T AI CONSTRUCTION CONSULTING & PROJECT MANAGEMENT"
    FOUNDER_NAME = "Mai Quang Vinh"

    # -------------------------------------------------------------
    # 1. BÁO CÁO RIÊNG BIỆT CHO TỪNG PHÒNG BAN (STANDALONE REPORT)
    # -------------------------------------------------------------
    @classmethod
    def generate_standalone_department_report(
        cls,
        workflow_type: str,
        result_data: Dict[str, Any],
        project_name: str = "Dự án Tổ hợp T&T Tower",
        export_docx: bool = True
    ) -> Dict[str, Any]:
        """
        Sinh báo cáo thẩm tra riêng biệt chuyên sâu khi người dùng chỉ yêu cầu chạy 1 quy trình.
        """
        wf = workflow_type.upper()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        dept_name = result_data.get("department", "Phòng Ban Chuyên Trách")
        gate_status = result_data.get("gate_status", "APPROVED_FOR_TRANSFER")
        personnel = result_data.get("personnel", {})
        specialist = personnel.get("specialist", "Chuyên viên chuyên môn")
        head = personnel.get("department_head", "Trưởng phòng kiểm duyệt")

        report_title = f"BÁO CÁO THẨM TRA NGHIỆP VỤ CHUYÊN SÂU: {dept_name.upper()}"
        report_code = f"BC-TT-{wf}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        attached_file = result_data.get("attached_file_name") or "Hồ sơ nhập trực tiếp trên hệ thống"
        attached_link = result_data.get("attached_file_link") or "Kho dữ liệu nội bộ dự án"

        # Xây dựng nội dung Markdown
        md_lines = [
            f"# 🏢 {cls.COMPANY_NAME}",
            f"## {report_title}",
            f"**Mã báo cáo:** `{report_code}` | **Thời gian lập:** {timestamp} | **Dự án:** {project_name}",
            f"**Người phê duyệt tối cao:** Founder / CEO {cls.FOUNDER_NAME} (Level 5)\n",
            "---",
            "### 📂 HỒ SƠ ĐẦU VÀO & HỘI ĐỒNG THẨM TRA PHÒNG BAN (2 CẤP NHÂN SỰ)",
            f"- 📄 **Tệp hồ sơ giao việc:** `{attached_file}`",
            f"- 🔗 **Đường link / Nguồn hồ sơ:** {attached_link}",
            f"- 👷 **Chuyên viên thực thi:** {specialist}",
            f"- 🧑‍⚖️ **Trưởng phòng kiểm duyệt:** {head}",
            f"- 🛡️ **LỆNH CHUYỂN BƯỚC (GATE CLEARANCE):** `[{gate_status}]` "
            f"{'✅ ĐỦ ĐIỀU KIỆN CHUYỂN BƯỚC' if gate_status == 'APPROVED_FOR_TRANSFER' else '🛑 CHẶN LẠI YÊU CẦU SỬA ĐỔI'}\n",
            "---",
            "### 🔍 NỘI DUNG THẨM TRA CHI TIẾT & KẾT QUẢ BÓC TÁCH"
        ]

        if wf == "CONTRACT":
            dossier = result_data.get("specialist_dossier", {})
            adv = dossier.get("advance_analysis", {})
            tpl = dossier.get("corporate_template_applied", {})
            md_lines.extend([
                f"- **Tên hợp đồng:** {result_data.get('contract_title', 'Hợp đồng xây dựng')}",
                f"- **Căn cứ pháp luật & Quy chế nội bộ:** {result_data.get('applicable_law', 'Nghị định 210/2026/NĐ-CP & QĐ 690/QĐ-TGĐ')}",
                f"- **Mẫu Hợp đồng chuẩn áp dụng:** `{tpl.get('code', 'XDTC.2024.01')}` - {tpl.get('name', '')} *(Kèm Cam kết chống tham nhũng `XDCK.2024.01`)*",
                f"- **Giá trị hợp đồng:** {adv.get('contract_value', 0):,.0f} VNĐ",
                f"- **Mức tạm ứng đề nghị:** {adv.get('requested_advance', 0):,.0f} VNĐ ({adv.get('advance_ratio_percent', 0)}%)",
                f"- **Bảo lãnh tạm ứng ngân hàng:** {'Đã có bảo lãnh (Hiệu lực >= Thời gian HĐ + 30 ngày theo QĐ 122/123)' if adv.get('has_bank_guarantee') else 'CHƯA CÓ THƯ BẢO LÃNH'}",
                "\n#### ⚠️ Danh mục cảnh báo bẫy điều khoản & vi phạm luật định:"
            ])
            for alert in result_data.get("critical_alerts", []):
                md_lines.append(f"  - **[{alert.get('severity', 'HIGH')}]** {alert.get('issue', '')} "
                                f"\n    *Căn cứ:* `{alert.get('legal_ground', '')}` "
                                f"\n    *Biện pháp:* **{alert.get('recommendation', '')}**")

        elif wf == "BIDDING":
            head_rev = result_data.get("head_review", {})
            md_lines.extend([
                f"- **Gói thầu:** {result_data.get('package_name', '')} (Loại: {result_data.get('package_type', '')})",
                f"- **Căn cứ pháp lý & Quy định LCNT:** {head_rev.get('applicable_law', 'Nghị định 349/2026/NĐ-CP & QĐ 419/QĐ-TGĐ')}",
                f"- **Mẫu HSMT chuẩn áp dụng (QĐ 458):** `{head_rev.get('recommended_hsmt_template', 'BM12 - HSMT Thi công Xây lắp')}`",
                f"- **Bộ biểu mẫu quy trình LCNT:** `BM0-PYC` -> `BM03-BBMT` -> `BM04-BCDGKT (Làm rõ tối đa 01 lần)` -> `BM05-BC Giá` -> `BM07-BBĐP` -> `BM08-TTr PDKQLCNT`",
                f"- **Giá trị dự toán gói thầu:** {result_data.get('estimated_budget', 0):,.0f} VNĐ",
                f"- **Hạn mức chỉ định thầu quy định:** {head_rev.get('direct_award_ceiling', 0):,.0f} VNĐ",
                f"- **Giá gói thầu đề xuất trao thầu:** {result_data.get('recommended_package_price', 0):,.0f} VNĐ",
                "\n#### 📊 Phân tích danh sách báo giá & loại trừ dị biệt (Lệch > 30%):"
            ])
            for q in head_rev.get("excluded_quotes", []):
                md_lines.append(f"  - 🚫 **Nhà thầu bị loại trừ:** {q.get('vendor', '')} - Chào: {q.get('price', 0):,.0f} VNĐ (Lệch {q.get('deviation_percent', 0)}%)\n    *Lý do:* {q.get('reason', '')}")
            for v in result_data.get("alerts", []):
                md_lines.append(f"  - ⚠️ **[{v.get('severity', 'HIGH')}]** {v.get('issue', '')}\n    *Căn cứ:* `{v.get('legal_ground', '')}`\n    *Yêu cầu:* **{v.get('action', '')}**")

        elif wf == "QS_BOQ":
            dossier = result_data.get("specialist_dossier", {})
            head_rev = result_data.get("head_review", {})
            md_lines.extend([
                f"- **Dự án:** {result_data.get('project_name', '')}",
                f"- **Căn cứ định mức & Quy trình:** {head_rev.get('applicable_law', 'Thông tư 09/2024/TT-BXD & Chuẩn hóa HSMT 8 Bill')}",
                f"- **Cấu trúc 8 Bill HSMT áp dụng:** `Bill 1 (CPC)` -> `Bill 2 (Trần CPC <= 5%)` -> `Bill 3 (BOQ)` -> `Bill 4 (Nguyên tắc đo bóc MIN khối lượng)` -> `Bill 5 (PL điều chỉnh)` -> `Bill 6 (Độ sụt BTTP)` -> `Bill 7 (Spec)` -> `Bill 8 (BV & PS)`",
                f"- **Quy trình xử lý phát sinh:** Tuân thủ 12 bước `QT01-XLPS` (`BM.01-QT01-XLPS` -> `BM.05-QT01-XLPS`, khẩn cấp xin chủ trương trong 24h)",
                f"- **Tổng số công tác thẩm tra:** {result_data.get('total_items', 0)} đầu việc",
                f"- **Tổng giá trị chi phí trực tiếp:** {result_data.get('total_boq_value', 0):,.0f} VNĐ *(Trần Chi phí hạng mục chung Bill 1 tối đa 5% = {result_data.get('max_general_cost_5pct', 0):,.0f} VNĐ)*",
                f"- **Số lỗi/bất thường phát hiện:** {result_data.get('anomalies_found', 0)} điểm",
                "\n#### ⚠️ Danh mục phát hiện tính trùng / lỗi định mức:"
            ])
            for anom in result_data.get("anomalies", []):
                md_lines.append(f"  - **[Dòng {anom.get('item_index', '')} - {anom.get('item_name', '')}]**: {anom.get('issue', '')}\n    *Biện pháp xử lý:* **{anom.get('remedy', '')}**")

        elif wf == "QAQC":
            head_rev = result_data.get("head_review", {})
            md_lines.extend([
                f"- **Hạng mục nghiệm thu:** {result_data.get('work_item', '')}",
                f"- **Ngày kiểm tra:** {result_data.get('inspection_date', '')}",
                f"- **Căn cứ quản lý chất lượng:** {head_rev.get('applicable_law', 'Nghị định 06/2021/NĐ-CP & Bộ 17 Biểu mẫu QA/QC')}",
                f"- **Biểu mẫu Checklist QA/QC bắt buộc:** `1.BM-PD NTP`, `2.BM-PD NCC`, `4.BM-PD PTN (LAS-XD)`, `7-8.BM-NTVL (CO/CQ)`, `9-10.BM-NTCVXD`, `12.BM-BBLMTN`, `13.BM-BBXNCVTC`, `15.BM-NKTC`",
                f"- **Điều kiện chuyển bước thi công:** {'ĐỦ ĐIỀU KIỆN' if result_data.get('can_proceed_to_next_phase') else 'CHƯA ĐỦ ĐIỀU KIỆN - ĐÌNH CHỈ'}",
                "\n#### ⚠️ Danh mục lỗi thủ tục / kỹ thuật nghiệm thu:"
            ])
            for d in result_data.get("defects", []):
                md_lines.append(f"  - 🚨 {d.get('issue', '')}\n    *Căn cứ:* `{d.get('rule', '')}`\n    *Lệnh:* **{d.get('order', '')}**")

        elif wf == "SETTLEMENT":
            dossier = result_data.get("specialist_dossier", {})
            head_rev = result_data.get("head_review", {})
            ktxd_scope = dossier.get("ktxd_audit_scope", {})
            md_lines.extend([
                f"- **Hợp đồng số:** {result_data.get('contract_no', '')}",
                f"- **Giá trị hợp đồng duyệt:** {result_data.get('contract_value', 0):,.0f} VNĐ",
                f"- **Lũy kế đề nghị thanh toán:** {dossier.get('cumulative_completed', 0):,.0f} VNĐ ({result_data.get('completion_ratio_percent', 0)}%)",
                f"- **Tỷ lệ thẩm định trọng yếu KTXD (QĐ 122/123):** Kiểm tra **{ktxd_scope.get('required_ktxd_audit_percent', 50)}%** giá trị các công tác chính ({ktxd_scope.get('stage', '')})",
                f"- **Biểu mẫu trình ký Founder:** `{head_rev.get('submission_form_code', 'BM-16.1 (Tờ trình CTĐH phê duyệt Thanh toán)')}` kèm `BM-07/BM-14 (BC thẩm định KTXD)`",
                f"- **Khấu trừ thu hồi tạm ứng:** {dossier.get('advance_recovered', 0):,.0f} VNĐ",
                f"- **Trích giữ bảo hành (5%):** {dossier.get('warranty_retained', 0):,.0f} VNĐ",
                f"- **THỰC THANH TOÁN KỲ NÀY:** **{dossier.get('net_payable_amount', 0):,.0f} VNĐ**",
                f"- **Căn cứ thanh toán:** {head_rev.get('applicable_law', 'Nghị định 99/2021/NĐ-CP & QĐ 122/123')}",
                "\n#### 🚨 Cảnh báo kiểm toán tài chính 4 tầng & Quy tắc 3 lỗi cơ bản QĐ 122/123:"
            ])
            for rf in result_data.get("red_flags", []):
                md_lines.append(f"  - ⚠️ **[{rf.get('severity', 'HIGH')}]** {rf.get('issue', '')}\n    *Căn cứ:* `{rf.get('legal_ground', '')}`\n    *Yêu cầu:* **{rf.get('action', '')}**")

        elif wf == "MARKETING":
            content_d = result_data.get("content_dossier", {})
            video_d = result_data.get("video_dossier", {})
            head_r = result_data.get("head_review", {})
            budget = head_r.get("campaign_budget", 0) if isinstance(head_r, dict) else 0
            md_lines.extend([
                f"- **Chiến dịch truyền thông:** {result_data.get('campaign_title', 'Chiến dịch Nâng tầm Thương hiệu')}",
                f"- **Chuyên viên Sáng tạo Nội dung:** {content_d.get('specialist', 'Trần Thị Lan Tỏa')}",
                f"- **Chuyên viên Dựng & Sản xuất Video:** {video_d.get('specialist', 'Nguyễn Huy Dựng')}",
                f"- **Trưởng ban kiểm duyệt:** {head_r.get('department_head', 'Lê Mai Truyền')}",
                f"- **Quy chuẩn nhận diện thương hiệu:** Chuẩn hóa Logo, Bảng màu T&T Navy/Gold, Bản quyền âm nhạc thương mại",
                f"- **Tổng số bài viết sáng tạo:** {content_d.get('posts_count', 0)} bài đăng đa kênh (Facebook, LinkedIn, Báo chí)",
                f"- **Thời lượng video quảng bá:** {video_d.get('duration_seconds', 60)} giây ({video_d.get('scenes_count', 0)} phân cảnh Storyboard)",
                f"- **Định dạng video sản xuất:** {', '.join(video_d.get('video_formats', ['9:16 Shorts/Reels', '16:9 4K']))}",
                "\n#### 📝 Danh mục bài viết sáng tạo (PR & Social Media):"
            ])
            for p in content_d.get("draft_posts", []):
                md_lines.extend([
                    f"  - 📢 **Kênh phát hành:** `{p.get('channel', '')}` — **Loại:** *{p.get('post_type', '')}*",
                    f"    *Tiêu đề:* **{p.get('title', '')}**",
                    f"    *Nội dung trích đoạn:* {p.get('content_preview', '')[:220]}...",
                    f"    *Hashtags:* `{' '.join(p.get('hashtags', []))}`"
                ])
            md_lines.extend([
                "\n#### 🎬 Kịch bản phân cảnh Video Clip (Storyboard):"
            ])
            for sc in video_d.get("storyboard", []):
                md_lines.append(
                    f"  - 🎞️ **Cảnh {sc.get('scene_number', '')} ({sc.get('time_range', '')}):** {sc.get('visual_description', '')}\n"
                    f"    *Voiceover AI:* \"{sc.get('audio_voiceover', '')}\"\n"
                    f"    *Góc máy & Âm nhạc:* {sc.get('camera_shot', '')} | BGM: {sc.get('music_bgm', '')}"
                )
            md_lines.extend([
                "\n#### 🛡️ Thẩm định rủi ro truyền thông & Quy chuẩn Gate Clearance:"
            ])
            for chk in head_r.get("compliance_checks", []):
                md_lines.append(f"  - [{chk.get('status', 'PASS')}] **{chk.get('check', '')}:** {chk.get('details', '')}")

        # Kết luận & Chữ ký
        md_lines.extend([
            "\n---",
            "### ⚖️ KẾT LUẬN & LỆNH ĐIỀU HÀNH PHÒNG BAN",
            f"**Trưởng phòng {head} phê chuẩn:**",
            f"> {result_data.get('summary', '')}",
            "\n| 👷 Chuyên viên thực thi | 🧑‍⚖️ Trưởng phòng kiểm duyệt | 👑 Founder / CEO phê duyệt |",
            "| :---: | :---: | :---: |",
            f"| *{specialist}* | *{head}* | *{cls.FOUNDER_NAME}* |",
            "| *(Đã bóc tách dữ liệu)* | *(Đã kiểm tra quy trình & Gate Clearance)* | *(Đã ký số phê duyệt)* |"
        ])

        markdown_content = "\n".join(md_lines)

        docx_path = None
        if export_docx:
            docx_path = os.path.join(REPORTS_DIR, f"{report_code}.docx")
            cls._export_markdown_to_docx(
                title=report_title,
                doc_code=report_code,
                dept_name=dept_name,
                markdown_text=markdown_content,
                output_path=docx_path
            )

        return {
            "report_type": "STANDALONE_DEPARTMENT",
            "workflow": wf,
            "department": dept_name,
            "report_code": report_code,
            "created_at": timestamp,
            "gate_status": gate_status,
            "markdown": markdown_content,
            "docx_path": docx_path
        }

    # -------------------------------------------------------------
    # 2. BÁO CÁO TỔNG HỢP CHUYÊN ĐỀ THEO YÊU CẦU (MODULAR REPORT)
    # -------------------------------------------------------------
    @classmethod
    def generate_modular_report(
        cls,
        selected_workflows: List[str],
        workflow_results: Dict[str, Any],
        report_theme: str = "Báo Cáo Tổng Hợp Nghiệp Vụ Chuyên Đề Theo Yêu Cầu",
        project_name: str = "Dự án Tổ hợp T&T Tower",
        export_docx: bool = True
    ) -> Dict[str, Any]:
        """
        Sinh báo cáo tổng hợp linh hoạt khi người dùng chỉ yêu cầu thực hiện một nhóm (1-4) quy trình.
        Chỉ tích hợp các phòng ban có trong selected_workflows, không tạo phòng ban thừa.
        """
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        report_code = f"BC-MODULAR-{len(selected_workflows)}WF-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"

        md_lines = [
            f"# 🏢 {cls.COMPANY_NAME}",
            f"## {report_theme.upper()}",
            f"**Mã báo cáo:** `{report_code}` | **Thời gian lập:** {timestamp} | **Dự án:** {project_name}",
            f"**Phạm vi thẩm tra:** {len(selected_workflows)} phòng ban được chỉ định: {', '.join([w.upper() for w in selected_workflows])}",
            f"**Chỉ đạo & Thẩm quyền:** Founder / CEO {cls.FOUNDER_NAME} (Level 5)\n",
            "---",
            "### 📊 BẢNG TỔNG HỢP TIẾN TRÌNH & LỆNH CHUYỂN BƯỚC (GATE CLEARANCE MATRIX)",
            "| STT | Phòng Ban Chuyên Trách | Nhân Sự Thực Thi & Kiểm Duyệt | Trạng Thái Lệnh Chuyển Bước | Hướng Xử Lý Kế Tiếp |",
            "| :---: | :--- | :--- | :---: | :--- |"
        ]

        total_alerts = 0
        all_passed = True

        for idx, wf in enumerate(selected_workflows, 1):
            wf_key = wf.upper()
            res = workflow_results.get(wf_key, {})
            dept_name = res.get("department", f"Phòng {wf_key}")
            gate = res.get("gate_status", "APPROVED_FOR_TRANSFER")
            personnel = res.get("personnel", {})
            head = personnel.get("department_head", "Trưởng phòng")
            summary = res.get("summary", "")

            if gate != "APPROVED_FOR_TRANSFER":
                all_passed = False

            gate_icon = "✅ ĐÃ DUYỆT" if gate == "APPROVED_FOR_TRANSFER" else "🛑 CHẶN LẠI"
            md_lines.append(f"| {idx} | **{dept_name}** | {head} | `{gate_icon}` | {summary[:80]}... |")

        md_lines.extend([
            "\n---",
            "### 📑 CHI TIẾT KẾT QUẢ THẨM TRA TỪNG PHÒNG BAN THEO CHỈ ĐỊNH\n"
        ])

        for idx, wf in enumerate(selected_workflows, 1):
            wf_key = wf.upper()
            res = workflow_results.get(wf_key, {})
            dept_name = res.get("department", f"Phòng {wf_key}")
            md_lines.append(f"#### {idx}. {dept_name.upper()}")
            md_lines.append(f"- **Tình trạng:** `{res.get('gate_status', 'UNKNOWN')}`")
            md_lines.append(f"- **Tóm tắt chuyên môn:** {res.get('summary', 'Chưa có tóm tắt.')}")

            # Thêm cảnh báo nếu có
            alerts = res.get("critical_alerts") or res.get("alerts") or res.get("anomalies") or res.get("defects") or res.get("red_flags") or []
            if alerts:
                total_alerts += len(alerts)
                md_lines.append(f"- **Phát hiện ({len(alerts)} điểm cần lưu ý):**")
                for a in alerts[:3]: # Lấy tối đa 3 điểm tiêu biểu
                    issue = a.get("issue") or a.get("violation") or "Vấn đề kỹ thuật"
                    md_lines.append(f"  * ⚠️ {issue}")
            md_lines.append("")

        # Phần kết luận chung
        md_lines.extend([
            "---",
            "### ⚖️ ĐÁNH GIÁ CHUNG & KẾT LUẬN CỦA FOUNDER / CEO",
            f"- **Đánh giá tổng thể:** {'Toàn bộ các quy trình được yêu cầu ĐÃ ĐẠT CHUẨN chuyển bước.' if all_passed else f'Phát hiện {total_alerts} điểm rủi ro. YÊU CẦU CÁC PHÒNG BAN HOÀN THIỆN trước khi thực hiện bước tiếp theo.'}",
            f"- **Chỉ đạo thực thi:** Bàn giao hồ sơ cho Founder {cls.FOUNDER_NAME} xem xét phê duyệt các nội dung thẩm quyền.",
            "\n| Người Tổng Hợp Hồ Sơ | Giám Sát Tuân Thủ Quy Trình | Phê Duyệt Của Founder |",
            "| :---: | :---: | :---: |",
            "| **AI Multi-Agent Orchestrator** | **Hội đồng Trưởng phòng** | **Mai Quang Vinh** |",
            "| *(Tự động tổng hợp)* | *(Ký kiểm duyệt Gate Clearance)* | *(Founder / CEO)* |"
        ])

        markdown_content = "\n".join(md_lines)

        docx_path = None
        if export_docx:
            docx_path = os.path.join(REPORTS_DIR, f"{report_code}.docx")
            cls._export_markdown_to_docx(
                title=report_theme,
                doc_code=report_code,
                dept_name="HỘI ĐỒNG THẨM TRA ĐA PHÒNG BAN THEO YÊU CẦU",
                markdown_text=markdown_content,
                output_path=docx_path
            )

        return {
            "report_type": "MODULAR_WORKFLOW",
            "selected_workflows": selected_workflows,
            "report_code": report_code,
            "created_at": timestamp,
            "all_passed": all_passed,
            "total_alerts": total_alerts,
            "markdown": markdown_content,
            "docx_path": docx_path
        }

    # -------------------------------------------------------------
    # 3. BỘ BẢN BÁO CÁO TỔNG THỂ CÔNG TY (MASTER EXECUTIVE DOSSIER)
    # -------------------------------------------------------------
    @classmethod
    def generate_master_company_report(
        cls,
        all_departments_results: Dict[str, Any],
        project_name: str = "Tổ hợp Thương mại & Văn phòng T&T Tower",
        project_code: str = "DA-TT-2026-HQ",
        export_docx: bool = True
    ) -> Dict[str, Any]:
        """
        Sinh Bản Báo Cáo Tổng Thể Toàn Diện của Công Ty (Master Executive Dossier)
        kèm đầy đủ báo cáo chuyên môn của toàn bộ 5 phòng ban:
        1. Pháp chế & Hợp đồng (NĐ 210/2026)
        2. Đấu thầu & Mua sắm (NĐ 349/2026)
        3. Dự toán QS & BOQ (TT 09/2024)
        4. Quản lý Chất lượng QA/QC (NĐ 06/2021)
        5. Kiểm toán Thanh Quyết toán (NĐ 99/2021)
        """
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        report_code = f"MASTER-DOSSIER-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        report_title = "BÁO CÁO THẨM TRA TỔNG THỂ DỰ ÁN & ĐIỀU HÀNH DOANH NGHIỆP XÂY DỰNG"

        # Tính toán các chỉ số tổng thể
        res_contract = all_departments_results.get("CONTRACT", {})
        res_bidding = all_departments_results.get("BIDDING", {})
        res_qs = all_departments_results.get("QS_BOQ", {})
        res_qaqc = all_departments_results.get("QAQC", {})
        res_settlement = all_departments_results.get("SETTLEMENT", {})
        res_marketing = all_departments_results.get("MARKETING", {})

        gates = [
            res_contract.get("gate_status", "PENDING"),
            res_bidding.get("gate_status", "PENDING"),
            res_qs.get("gate_status", "PENDING"),
            res_qaqc.get("gate_status", "PENDING"),
            res_settlement.get("gate_status", "PENDING"),
            res_marketing.get("gate_status", "PENDING")
        ]
        approved_count = sum(1 for g in gates if g == "APPROVED_FOR_TRANSFER")
        blocked_count = sum(1 for g in gates if g == "BLOCKED_REVISE")

        contract_val = res_contract.get("specialist_dossier", {}).get("advance_analysis", {}).get("contract_value", 0) or 15_000_000_000
        settlement_paid = res_settlement.get("specialist_dossier", {}).get("net_payable_amount", 0) or 1_500_000_000

        md_lines = [
            f"# 🏢 {cls.COMPANY_NAME}",
            f"## {report_title.upper()}",
            f"**Mã hồ sơ tổng thể:** `{report_code}` | **Dự án:** {project_name} (`{project_code}`)",
            f"**Thời gian xuất bản:** {timestamp} | **Phạm vi:** TOÀN DIỆN 6 PHÒNG BAN CHUYÊN MÔN",
            f"**Người phê duyệt tối cao:** Founder / CEO {cls.FOUNDER_NAME} (Level 5)\n",
            "---",
            "### 🏛️ PHẦN I: TỔNG QUAN ĐIỀU HÀNH & MA TRẬN CHUYỂN BƯỚC (EXECUTIVE SUMMARY)",
            f"- **Chỉ số sức khỏe dự án:** Đạt {approved_count}/6 phòng ban được cấp lệnh chuyển bước ({int(approved_count/6*100)}%).",
            f"- **Số phòng ban bị chặn lại để sửa đổi:** {blocked_count} phòng ban.",
            f"- **Tổng giá trị hợp đồng quản lý:** {contract_val:,.0f} VNĐ.",
            f"- **Tổng giá trị giải ngân đề xuất:** {settlement_paid:,.0f} VNĐ.",
            "\n#### 📋 Bảng Tổng Hợp Kiểm Soát 6 Phòng Ban (Pháp Luật 2026 & Quy Chế Tập Đoàn):",
            "| STT | Phòng Ban | Chuyên Viên Thực Thi | Trưởng Phòng Kiểm Duyệt | Pháp Luật 2026 & Quy Chế Nội Bộ | Lệnh Chuyển Bước |",
            "| :---: | :--- | :--- | :--- | :--- | :---: |",
            f"| 1 | **Pháp chế & Hợp đồng** | Nguyễn Văn Pháp | Trần Thị Tuân Thủ | NĐ 210/2026 & Mẫu QĐ 690/560 | `[{res_contract.get('gate_status', 'N/A')}]` |",
            f"| 2 | **Đấu thầu & Mua sắm** | Lê Quang Thầu | Phạm Minh Đấu | NĐ 349/2026 & QĐ 419/458 (HSMT) | `[{res_bidding.get('gate_status', 'N/A')}]` |",
            f"| 3 | **Dự toán QS & BOQ** | Đỗ Văn Lượng | Vũ Đình Toàn | TT 09/2024 & 8 Bill HSMT / QT01-XLPS | `[{res_qs.get('gate_status', 'N/A')}]` |",
            f"| 4 | **Quản lý Chất lượng QA/QC** | Bùi Văn Nghiệm | Hoàng Văn Chuẩn | NĐ 06/2021 & Checklist 17 BM QA/QC | `[{res_qaqc.get('gate_status', 'N/A')}]` |",
            f"| 5 | **Kiểm toán Thanh Quyết toán** | Ngô Thị Quyết | Đặng Đức Toán | NĐ 99/2021 & QĐ 122/123 (BM-16.1) | `[{res_settlement.get('gate_status', 'N/A')}]` |",
            f"| 6 | **Marketing & Truyền thông** | Trần Thị Lan Tỏa & Nguyễn Huy Dựng | Lê Mai Truyền | Quy chuẩn T&T & Chiến lược Đa kênh | `[{res_marketing.get('gate_status', 'N/A')}]` |",
            "\n---",
            "### 📑 PHẦN II: BÁO CÁO CHUYÊN MÔN CHI TIẾT TỪNG PHÒNG BAN",
            "\n#### 1. BAN PHÁP CHẾ & HỢP ĐỒNG (LEGAL & CONTRACT)",
            f"- **Chuyên viên:** {res_contract.get('personnel', {}).get('specialist', 'Nguyễn Văn Pháp')}",
            f"- **Trưởng phòng kiểm duyệt:** {res_contract.get('personnel', {}).get('department_head', 'Trần Thị Tuân Thủ')}",
            f"- **Lệnh chuyển bước:** `[{res_contract.get('gate_status', 'N/A')}]`",
            f"- **Nội dung:** {res_contract.get('summary', '')}",
            "- **Các cảnh báo pháp lý trọng yếu:**"
        ]

        for a in res_contract.get("critical_alerts", []):
            md_lines.append(f"  * ⚠️ **[{a.get('severity', 'HIGH')}]** {a.get('issue', '')} (Căn cứ: `{a.get('legal_ground', '')}`)")

        md_lines.extend([
            "\n#### 2. BAN ĐẤU THẦU & MUA SẮM THIẾT BỊ (BIDDING & PROCUREMENT)",
            f"- **Chuyên viên:** {res_bidding.get('personnel', {}).get('specialist', 'Lê Quang Thầu')}",
            f"- **Trưởng phòng kiểm duyệt:** {res_bidding.get('personnel', {}).get('department_head', 'Phạm Minh Đấu')}",
            f"- **Lệnh chuyển bước:** `[{res_bidding.get('gate_status', 'N/A')}]`",
            f"- **Giá gói thầu đề xuất trao thầu:** {res_bidding.get('recommended_package_price', 0):,.0f} VNĐ",
            f"- **Nội dung:** {res_bidding.get('summary', '')}",
            "- **Tình trạng báo giá:**"
        ])
        for q in res_bidding.get("head_review", {}).get("excluded_quotes", []):
            md_lines.append(f"  * 🚫 Loại trừ báo giá {q.get('vendor', '')}: Lệch {q.get('deviation_percent', 0)}% > 30% theo NĐ 349/2026.")

        md_lines.extend([
            "\n#### 3. BAN KỸ SƯ DỰ TOÁN QS & BÓC TÁCH BOQ (COST ESTIMATING)",
            f"- **Chuyên viên:** {res_qs.get('personnel', {}).get('specialist', 'Đỗ Văn Lượng')}",
            f"- **Trưởng phòng kiểm duyệt:** {res_qs.get('personnel', {}).get('department_head', 'Vũ Đình Toàn')}",
            f"- **Lệnh chuyển bước:** `[{res_qs.get('gate_status', 'N/A')}]`",
            f"- **Tổng giá trị BOQ sau thẩm tra:** {res_qs.get('total_boq_value', 0):,.0f} VNĐ",
            f"- **Nội dung:** {res_qs.get('summary', '')}",
            "- **Phát hiện gian lận / trùng lặp:**"
        ])
        for an in res_qs.get("anomalies", []):
            md_lines.append(f"  * ⚠️ {an.get('issue', '')} -> Biện pháp: {an.get('remedy', '')}")

        md_lines.extend([
            "\n#### 4. BAN QUẢN LÝ CHẤT LƯỢNG QA/QC HIỆN TRƯỜNG (SITE QUALITY & OPERATIONS)",
            f"- **Chuyên viên:** {res_qaqc.get('personnel', {}).get('specialist', 'Bùi Văn Nghiệm')}",
            f"- **Trưởng phòng kiểm duyệt:** {res_qaqc.get('personnel', {}).get('department_head', 'Hoàng Văn Chuẩn')}",
            f"- **Lệnh chuyển bước:** `[{res_qaqc.get('gate_status', 'N/A')}]`",
            f"- **Quyết định cho phép thi công:** {'ĐỦ ĐIỀU KIỆN' if res_qaqc.get('can_proceed_to_next_phase') else 'ĐÌNH CHỈ / KHÔNG ĐỦ ĐIỀU KIỆN'}",
            f"- **Nội dung:** {res_qaqc.get('summary', '')}"
        ])

        md_lines.extend([
            "\n#### 5. BAN KIỂM TOÁN THANH & QUYẾT TOÁN (SETTLEMENT & DISBURSEMENT AUDIT)",
            f"- **Chuyên viên:** {res_settlement.get('personnel', {}).get('specialist', 'Ngô Thị Quyết')}",
            f"- **Trưởng phòng kiểm duyệt:** {res_settlement.get('personnel', {}).get('department_head', 'Đặng Đức Toán')}",
            f"- **Lệnh chuyển bước:** `[{res_settlement.get('gate_status', 'N/A')}]`",
            f"- **Giá trị thực thanh toán kỳ này (Mẫu 08a):** {res_settlement.get('specialist_dossier', {}).get('net_payable_amount', 0):,.0f} VNĐ",
            f"- **Nội dung:** {res_settlement.get('summary', '')}"
        ])

        res_mkt_content = res_marketing.get("content_dossier", {})
        res_mkt_video = res_marketing.get("video_dossier", {})
        md_lines.extend([
            "\n#### 6. BAN MARKETING & TRUYỀN THÔNG THƯƠNG HIỆU (MARKETING & MEDIA)",
            f"- **Chuyên viên Sáng tạo Bài viết:** {res_marketing.get('personnel', {}).get('specialist_content', 'Trần Thị Lan Tỏa')}",
            f"- **Chuyên viên Thiết kế & Dựng Video:** {res_marketing.get('personnel', {}).get('specialist_video', 'Nguyễn Huy Dựng')}",
            f"- **Trưởng ban kiểm duyệt:** {res_marketing.get('personnel', {}).get('department_head', 'Lê Mai Truyền')}",
            f"- **Lệnh chuyển bước:** `[{res_marketing.get('gate_status', 'N/A')}]`",
            f"- **Chiến dịch đề xuất:** {res_marketing.get('campaign_title', 'Chiến dịch Nâng tầm Thương hiệu')}",
            f"- **Số lượng bài viết & kịch bản:** {res_mkt_content.get('posts_count', 0)} bài đăng đa kênh & {res_mkt_video.get('scenes_count', 0)} phân cảnh Storyboard",
            f"- **Nội dung:** {res_marketing.get('summary', '')}"
        ])

        md_lines.extend([
            "\n---",
            "### 👑 PHẦN III: QUYẾT NGHỊ VÀ PHÊ DUYỆT CỦA FOUNDER / CEO",
            f"Căn cứ kết quả thẩm tra 6 phòng ban, Founder / CEO **{cls.FOUNDER_NAME}** phê chuẩn:",
            f"1. **Chấp thuận kết quả chuyển bước** của các phòng ban đạt chuẩn (`APPROVED_FOR_TRANSFER`).",
            "2. **Yêu cầu đàm phán sửa đổi** các điều khoản hợp đồng vi phạm Nghị định 210/2026/NĐ-CP trước khi ký kết chính thức.",
            "3. **Phê duyệt hạn mức giải ngân** theo Mẫu 08a sau khi đã khấu trừ tạm ứng và bảo hành 5% đúng quy định.",
            "4. **Phê duyệt chiến dịch truyền thông đa kênh** và phát hành các ấn phẩm, video quảng bá hình ảnh doanh nghiệp.",
            "\n| BAN KIỂM SOÁT THẨM TRA | TRƯỞNG BAN ĐIỀU PHỐI AI | CHỦ TỊCH / CEO PHÊ DUYỆT |",
            "| :---: | :---: | :---: |",
            "| **Hội đồng 6 Trưởng ban** | **Multi-Agent Orchestrator** | **Mai Quang Vinh** |",
            "| *(Ký tên và đóng dấu chuyên môn)* | *(Tự động tổng hợp và kiểm toán)* | *(Ký duyệt cao nhất & Chịu trách nhiệm pháp lý)* |"
        ])

        markdown_content = "\n".join(md_lines)

        docx_path = None
        if export_docx:
            docx_path = os.path.join(REPORTS_DIR, f"{report_code}.docx")
            cls._export_markdown_to_docx(
                title=report_title,
                doc_code=report_code,
                dept_name="HỘI ĐỒNG THẨM TRA TỔNG THỂ CÔNG TY",
                markdown_text=markdown_content,
                output_path=docx_path
            )

        return {
            "report_type": "MASTER_COMPANY_REPORT",
            "report_code": report_code,
            "created_at": timestamp,
            "project_name": project_name,
            "project_code": project_code,
            "approved_departments": approved_count,
            "blocked_departments": blocked_count,
            "contract_value": contract_val,
            "net_payable": settlement_paid,
            "markdown": markdown_content,
            "docx_path": docx_path
        }

    # -------------------------------------------------------------
    # HELPER: CHUYỂN ĐỔI MARKDOWN THÀNH FILE WORD (.DOCX) CHUẨN NĐ 30/2020
    # -------------------------------------------------------------
    @classmethod
    def _export_markdown_to_docx(
        cls,
        title: str,
        doc_code: str,
        dept_name: str,
        markdown_text: str,
        output_path: str
    ):
        doc = docx.Document()

        # Định dạng lề trang chuẩn NĐ 30/2020: Trên 20mm, Dưới 20mm, Trái 30mm, Phải 15mm
        section = doc.sections[0]
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)

        # Header 2 cột
        table = doc.add_table(rows=2, cols=2)
        table.autofit = True

        c00 = table.cell(0, 0)
        p00 = c00.paragraphs[0]
        p00.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_org = p00.add_run(cls.COMPANY_NAME)
        r_org.bold = True
        r_org.font.name = "Times New Roman"
        r_org.font.size = Pt(10)

        c10 = table.cell(1, 0)
        p10 = c10.paragraphs[0]
        p10.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_code = p10.add_run(f"Số: {doc_code}")
        r_code.font.name = "Times New Roman"
        r_code.font.size = Pt(10)

        c01 = table.cell(0, 1)
        p01 = c01.paragraphs[0]
        p01.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_qh = p01.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM")
        r_qh.bold = True
        r_qh.font.name = "Times New Roman"
        r_qh.font.size = Pt(10)

        c11 = table.cell(1, 1)
        p11 = c11.paragraphs[0]
        p11.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_tn = p11.add_run("Độc lập - Tự do - Hạnh phúc")
        r_tn.bold = True
        r_tn.underline = True
        r_tn.font.name = "Times New Roman"
        r_tn.font.size = Pt(11)

        doc.add_paragraph() # Dòng trống

        # Tiêu đề báo cáo
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_t = p_title.add_run(title.upper())
        r_t.bold = True
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(13)
        r_t.font.color.rgb = RGBColor(30, 58, 138)

        # Trích yếu
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sub = p_sub.add_run(f"(Đơn vị thực hiện: {dept_name} - Phê duyệt: Founder {cls.FOUNDER_NAME})")
        r_sub.italic = True
        r_sub.font.name = "Times New Roman"
        r_sub.font.size = Pt(11)

        # Duyệt qua các dòng markdown để dựng nội dung Word
        lines = markdown_text.split("\n")
        in_table = False
        table_rows = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Bỏ qua tiêu đề cấp 1 và 2 vì đã có ở header
            if line_str.startswith("# ") or line_str.startswith("## "):
                continue

            # Bảng Markdown
            if line_str.startswith("|"):
                if "---" in line_str:
                    continue
                parts = [p.strip() for p in line_str.split("|")[1:-1]]
                table_rows.append(parts)
                in_table = True
                continue
            else:
                if in_table and table_rows:
                    # Ghi bảng vào tài liệu Word
                    w_tbl = doc.add_table(rows=len(table_rows), cols=len(table_rows[0]))
                    w_tbl.style = 'Table Grid'
                    for r_idx, row_data in enumerate(table_rows):
                        for c_idx, cell_text in enumerate(row_data):
                            c = w_tbl.cell(r_idx, c_idx)
                            c.text = cell_text.replace("**", "").replace("*", "")
                            p = c.paragraphs[0]
                            p.runs[0].font.name = "Times New Roman"
                            p.runs[0].font.size = Pt(9.5)
                            if r_idx == 0:
                                p.runs[0].bold = True
                    table_rows = []
                    in_table = False
                    doc.add_paragraph()

            # Tiêu đề mục h3, h4
            if line_str.startswith("### "):
                p = doc.add_paragraph()
                r = p.add_run(line_str.replace("### ", "").replace("**", ""))
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.font.color.rgb = RGBColor(14, 116, 144)
            elif line_str.startswith("#### "):
                p = doc.add_paragraph()
                r = p.add_run(line_str.replace("#### ", "").replace("**", ""))
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
            elif line_str.startswith("- ") or line_str.startswith("* "):
                p = doc.add_paragraph(style='List Bullet')
                r = p.add_run(line_str[2:].replace("**", "").replace("*", ""))
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
            elif line_str.startswith("> "):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                r = p.add_run(line_str[2:].replace("**", ""))
                r.italic = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(10.5)
            else:
                p = doc.add_paragraph()
                r = p.add_run(line_str.replace("**", ""))
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)

        # Lưu file
        doc.save(output_path)
        return output_path

# Global singleton
reporting_engine = ConstructionReportingEngine()
