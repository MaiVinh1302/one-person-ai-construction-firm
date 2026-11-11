# -*- coding: utf-8 -*-
"""
DEPARTMENT 4: Quality Management & Site Operations (Phòng Quản lý Chất lượng QA/QC)
Cơ cấu 2 cấp nhân sự:
1. Kỹ sư QA/QC Hiện trường: Bùi Văn Nghiệm (Specialist Execution Agent)
   - Thu thập nhật ký thi công (15.BM-NKTC), kiểm tra phiếu nén mẫu R28 (12.BM-BBLMTN), đối chiếu Bộ 17 Biểu mẫu Checklist QA/QC Tập đoàn (1.BM-PD NTP -> 17.BM-BBNTHT).
2. Trưởng phòng QA/QC: Hoàng Văn Chuẩn (Department Head Reviewing Agent)
   - Rà soát quy trình nghiệm thu Điều 13 NĐ 06/2021/NĐ-CP, mẫu dấu hoàn công 4 bên Phụ lục II, thẩm quyền ký Shopdrawing/BPTC theo Bill 8 HSMT, và quy định ghi rõ ngày tháng/đối tượng nghiệm thu theo QĐ 122/123.
   - Quyết định Gate Clearance (Lệnh chấp thuận chuyển bước thi công & chuyển hồ sơ sang Ban Quyết toán).
"""

from typing import Dict, List, Any
from core.permissions import RoleLevel
from knowledge.corporate_sops import QAQC_17_CHECKLIST_TEMPLATES

class SiteQCSpecialistAgent:
    """
    KỸ SƯ QA/QC HIỆN TRƯỜNG: BÙI VĂN NGHIỆM (Level 2 Specialist)
    Chuyên trách kiểm tra hồ sơ hiện trường, kết quả thí nghiệm và lập hồ sơ theo Bộ 17 Biểu mẫu Checklist QA/QC Tập đoàn.
    """
    AGENT_NAME = "Bùi Văn Nghiệm"
    ROLE_TITLE = "Kỹ sư QA/QC Giám sát Hiện trường & Hồ sơ Nghiệm thu"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def execute_field_inspection(
        cls,
        work_item: str,
        inspection_date: str,
        test_results_passed: bool,
        logbook_updated: bool,
        asbuilt_stamp_signatures: List[str]
    ) -> Dict[str, Any]:
        
        field_notes = []
        if test_results_passed:
            field_notes.append("Phiếu thí nghiệm kết quả nén mẫu/thử tải đạt yêu cầu thiết kế (Kèm 4.BM-PD PTN LAS-XD, 7-8.BM-NTVL CO/CQ và 12.BM-BBLMTN).")
        else:
            field_notes.append("CẢNH BÁO: Thí nghiệm vật liệu / cường độ mẫu chưa đạt hoặc thiếu hồ sơ CO/CQ (8.BM-NTVL), kết quả thí nghiệm.")

        if logbook_updated:
            field_notes.append("Nhật ký thi công (15.BM-NKTC) và Nhật ký ATLĐ (16.BM-NKATLĐ) đã ghi nhận đầy đủ thời tiết, nhân lực, thiết bị.")
        else:
            field_notes.append("Nhật ký thi công (15.BM-NKTC) ngày nghiệm thu còn để trống.")

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "execution_status": "COMPLETED",
            "work_item": work_item,
            "inspection_date": inspection_date,
            "test_results_passed": test_results_passed,
            "logbook_updated": logbook_updated,
            "signatures_collected": asbuilt_stamp_signatures,
            "qaqc_17_checklist": QAQC_17_CHECKLIST_TEMPLATES,
            "field_notes": field_notes,
            "summary_note": (
                f"Kỹ sư {cls.AGENT_NAME} đã lập hồ sơ nghiệm thu hạng mục '{work_item}' theo Bộ 17 Biểu mẫu QA/QC Tập đoàn "
                f"(9-10.BM-NTCVXD, 13.BM-BBXNCVTC, 15.BM-NKTC). Sẵn sàng trình Trưởng phòng thẩm tra."
            )
        }


class QAQCHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG QA/QC: HOÀNG VĂN CHUẨN (Level 3 Head)
    Chuyên trách kiểm duyệt quy trình nghiệm thu NĐ 06/2021, Checklist 17 Biểu mẫu TQT và ban hành LỆNH CHUYỂN BƯỚC.
    """
    AGENT_NAME = "Hoàng Văn Chuẩn"
    ROLE_TITLE = "Trưởng phòng Quản lý Chất lượng & An toàn Công trình"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    REQUIRED_SIGNATURES_ASBUILT = [
        "Người lập bản vẽ hoàn công",
        "Người đại diện theo pháp luật của Nhà thầu thi công xây dựng",
        "Người đại diện theo pháp luật của Nhà thầu tư vấn giám sát",
        "Chủ nhiệm giám sát thi công xây dựng"
    ]

    @classmethod
    def review_and_gate_clearance(
        cls,
        specialist_dossier: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        work_item = specialist_dossier.get("work_item", "")
        inspection_date = specialist_dossier.get("inspection_date", "")
        test_passed = specialist_dossier.get("test_results_passed", False)
        log_updated = specialist_dossier.get("logbook_updated", False)
        collected_sigs = specialist_dossier.get("signatures_collected", [])

        compliance_checks = []
        defects = []

        # 0. Rà soát quy tắc QĐ 122/123: BB nghiệm thu/Shopdrawing/BVHC không được thiếu ngày tháng hoặc ghi đối tượng chung chung
        if not inspection_date or not work_item or len(work_item.strip()) < 5:
            defects.append({
                "rule": "Quy định TQT QĐ 122/123 (Lỗi cơ bản từ chối tiếp nhận hồ sơ)",
                "issue": "Biên bản nghiệm thu (10.BM-NTCVXD) thiếu ngày tháng cụ thể hoặc ghi tên đối tượng nghiệm thu chung chung.",
                "order": "Bắt buộc ghi rõ vị trí, trục, tầng, cao độ nghiệm thu và ngày tháng đầy đủ trên 10.BM-NTCVXD & 13.BM-BBXNCVTC."
            })

        # 1. Rà soát kết quả thí nghiệm theo Điều 13 Nghị định 06/2021/NĐ-CP & 4.BM-PD PTN / 7-8.BM-NTVL
        if not test_passed:
            defects.append({
                "rule": "Khoản 1 Điều 13 Nghị định 06/2021/NĐ-CP & Biểu mẫu 7-8.BM-NTVL, 12.BM-BBLMTN",
                "issue": f"Chưa có kết quả thí nghiệm đạt chuẩn hoặc thiếu CO/CQ đầu vào cho hạng mục '{work_item}'.",
                "order": "DỪNG NGHIỆM THU NGAY LẬP TỨC. Tuyệt đối không cho phép thi công công đoạn tiếp theo."
            })
            compliance_checks.append({
                "check": "KẾT QUẢ THÍ NGHIỆM LAS-XD & HỒ SƠ VẬT LIỆU (7-8.BM-NTVL)",
                "status": "FAIL",
                "details": "Chưa có kết quả hoặc kết quả không đạt"
            })
        else:
            compliance_checks.append({
                "check": "KẾT QUẢ THÍ NGHIỆM LAS-XD & HỒ SƠ VẬT LIỆU (7-8.BM-NTVL)",
                "status": "PASS",
                "details": "Đầy đủ phê duyệt NCC (2.BM-PD NCC), PTN (4.BM-PD PTN) và KQTN đạt chuẩn"
            })

        # 2. Rà soát nhật ký thi công theo Thông tư 10/2021/TT-BXD & 15.BM-NKTC
        if not log_updated:
            defects.append({
                "rule": "Thông tư 10/2021/TT-BXD & Mẫu 15.BM-NKTC / 16.BM-NKATLĐ",
                "issue": "Nhật ký thi công (15.BM-NKTC) chưa được hoàn thiện và ký xác nhận của các bên liên quan.",
                "order": "Yêu cầu TVGS và Chỉ huy trưởng ký đóng dấu nhật ký trước khi ký Biên bản nghiệm thu (10.BM-NTCVXD)."
            })
            compliance_checks.append({
                "check": "NHẬT KÝ THI CÔNG TT 10/2021 & MẪU 15.BM-NKTC",
                "status": "FAIL",
                "details": "Chưa ký nhật ký"
            })
        else:
            compliance_checks.append({
                "check": "NHẬT KÝ THI CÔNG TT 10/2021 & MẪU 15.BM-NKTC",
                "status": "PASS",
                "details": "Nhật ký thi công 15.BM-NKTC ghi chép đầy đủ đúng quy trình"
            })

        # 3. Rà soát mẫu dấu hoàn công 4 bên theo Phụ lục II Nghị định 06/2021/NĐ-CP & Bill 8 HSMT
        missing_sigs = []
        for req_sig in cls.REQUIRED_SIGNATURES_ASBUILT:
            found = any(req_sig.lower() in s.lower() for s in collected_sigs)
            if not found:
                missing_sigs.append(req_sig)

        if missing_sigs:
            defects.append({
                "rule": "Phụ lục II Nghị định số 06/2021/NĐ-CP & Bill 8 Chuẩn hóa HSMT",
                "issue": f"Mẫu dấu Bản vẽ hoàn công thiếu chữ ký hợp pháp của: {missing_sigs}.",
                "order": "Thu hồi bản vẽ để bổ sung đủ chữ ký chức danh, chữ ký nháy từng trang và mộc pháp nhân."
            })
            compliance_checks.append({
                "check": "MẪU DẤU HOÀN CÔNG PHỤ LỤC II NĐ 06/2021 & BILL 8 HSMT",
                "status": "FAIL",
                "details": f"Thiếu {len(missing_sigs)} chữ ký bắt buộc"
            })
        else:
            compliance_checks.append({
                "check": "MẪU DẤU HOÀN CÔNG PHỤ LỤC II NĐ 06/2021 & BILL 8 HSMT",
                "status": "PASS",
                "details": "Đầy đủ 4 chữ ký hợp pháp trên dấu hoàn công và Shopdrawing được duyệt"
            })

        # 4. Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        is_blocked = len(defects) > 0
        gate_status = "BLOCKED_REVISE" if is_blocked else "APPROVED_FOR_TRANSFER"

        next_step = ""
        if is_blocked:
            next_step = f"CHẶN CHUYỂN BƯỚC THI CÔNG. Phát hiện {len(defects)} lỗi quy trình QA/QC. Yêu cầu Kỹ sư Bùi Văn Nghiệm lập biên bản đình chỉ/khắc phục tại hiện trường."
        else:
            next_step = (
                "BAN HÀNH LỆNH CHUYỂN BƯỚC THI CÔNG (Hoàn tất bộ 17 Biểu mẫu Checklist QA/QC: 10.BM-NTCVXD, 13.BM-BBXNCVTC, 15.BM-NKTC). "
                "Đủ điều kiện bàn giao sang Ban Kiểm toán Thanh Quyết toán."
            )

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": "Nghị định 06/2021/NĐ-CP, Thông tư 10/2021/TT-BXD & Bộ 17 Biểu mẫu Checklist QA/QC Tập đoàn",
            "can_proceed": not is_blocked,
            "compliance_checks": compliance_checks,
            "defects_count": len(defects),
            "defects": defects,
            "gate_clearance_signoff": {
                "signer": cls.AGENT_NAME,
                "decision": gate_status,
                "next_step": next_step
            },
            "review_summary": f"Trưởng phòng {cls.AGENT_NAME}: {'CHẶN CHUYỂN BƯỚC DO VI PHẠM CHẤT LƯỢNG' if is_blocked else 'PHÊ DUYỆT CHUYỂN BƯỚC THI CÔNG & THANH TOÁN'}. {next_step}"
        }


class QAQCSiteDepartment:
    """
    WRAPPER PHÒNG BAN: Tích hợp 2 cấp Chuyên viên & Trưởng phòng
    """
    DEPARTMENT_NAME = "Phòng Quản lý Chất lượng QA/QC (Quality & Site)"

    @classmethod
    def audit_inspection_record(
        cls,
        work_item: str,
        inspection_date: str,
        test_results_passed: bool,
        logbook_updated: bool,
        asbuilt_stamp_signatures: List[str]
    ) -> Dict[str, Any]:
        
        # BƯỚC 1: Chuyên viên hiện trường thu thập dữ liệu & lập hồ sơ theo 17 Biểu mẫu QA/QC
        specialist_dossier = SiteQCSpecialistAgent.execute_field_inspection(
            work_item=work_item,
            inspection_date=inspection_date,
            test_results_passed=test_results_passed,
            logbook_updated=logbook_updated,
            asbuilt_stamp_signatures=asbuilt_stamp_signatures
        )

        # BƯỚC 2: Trưởng phòng rà soát quy trình, quy chuẩn NĐ 06/2021 & Checklist 17 BM, cấp lệnh chuyển bước
        head_review = QAQCHeadReviewerAgent.review_and_gate_clearance(specialist_dossier)

        return {
            "department": cls.DEPARTMENT_NAME,
            "status": "COMPLETED",
            "personnel": {
                "specialist": f"{SiteQCSpecialistAgent.AGENT_NAME} ({SiteQCSpecialistAgent.ROLE_TITLE})",
                "department_head": f"{QAQCHeadReviewerAgent.AGENT_NAME} ({QAQCHeadReviewerAgent.ROLE_TITLE})"
            },
            "work_item": work_item,
            "inspection_date": inspection_date,
            "specialist_dossier": specialist_dossier,
            "head_review": head_review,
            "gate_status": head_review.get("gate_status"),
            "can_proceed_to_next_phase": head_review.get("can_proceed", False),
            "defects_count": head_review.get("defects_count", 0),
            "defects": head_review.get("defects", []),
            "summary": f"[{head_review.get('gate_status')}] {head_review.get('review_summary')}"
        }
