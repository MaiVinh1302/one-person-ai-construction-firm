# -*- coding: utf-8 -*-
"""
DEPARTMENT 4: Quality Management & Site Operations (Phòng Quản lý Chất lượng QA/QC)
Cơ cấu 2 cấp nhân sự:
1. Kỹ sư QA/QC Hiện trường: Bùi Văn Nghiệm (Specialist Execution Agent)
   - Thu thập nhật ký thi công, kiểm tra phiếu nén mẫu R28, soạn dự thảo BBNTCV.
2. Trưởng phòng QA/QC: Hoàng Văn Chuẩn (Department Head Reviewing Agent)
   - Rà soát quy trình nghiệm thu Điều 13 NĐ 06/2021/NĐ-CP, kiểm tra mẫu dấu hoàn công 4 bên Phụ lục II.
   - Quyết định Gate Clearance (Lệnh chấp thuận chuyển bước thi công & chuyển hồ sơ sang Ban Quyết toán).
"""

from typing import Dict, List, Any
from core.permissions import RoleLevel

class SiteQCSpecialistAgent:
    """
    KỸ SƯ QA/QC HIỆN TRƯỜNG: BÙI VĂN NGHIỆM (Level 2 Specialist)
    Chuyên trách kiểm tra hồ sơ hiện trường, kết quả thí nghiệm và lập dự thảo BBNTCV.
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
            field_notes.append("Phiếu thí nghiệm kết quả nén mẫu/thử tải đạt yêu cầu thiết kế.")
        else:
            field_notes.append("CẢNH BÁO: Thí nghiệm vật liệu / cường độ mẫu chưa đạt hoặc chưa có phiếu kết quả.")

        if logbook_updated:
            field_notes.append("Nhật ký thi công đã ghi nhận điều kiện thời tiết, nhân lực, thiết bị đầy đủ.")
        else:
            field_notes.append("Nhật ký thi công ngày nghiệm thu còn để trống.")

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "execution_status": "COMPLETED",
            "work_item": work_item,
            "inspection_date": inspection_date,
            "test_results_passed": test_results_passed,
            "logbook_updated": logbook_updated,
            "signatures_collected": asbuilt_stamp_signatures,
            "field_notes": field_notes,
            "summary_note": f"Kỹ sư {cls.AGENT_NAME} đã lập hồ sơ kiểm tra cho hạng mục '{work_item}'. Sẵn sàng trình Trưởng phòng thẩm tra."
        }


class QAQCHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG QA/QC: HOÀNG VĂN CHUẨN (Level 3 Head)
    Chuyên trách kiểm duyệt quy trình nghiệm thu, quy chuẩn NĐ 06/2021 và ban hành LỆNH CHUYỂN BƯỚC.
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
        test_passed = specialist_dossier.get("test_results_passed", False)
        log_updated = specialist_dossier.get("logbook_updated", False)
        collected_sigs = specialist_dossier.get("signatures_collected", [])

        compliance_checks = []
        defects = []

        # 1. Rà soát kết quả thí nghiệm theo Điều 13 Nghị định 06/2021/NĐ-CP
        if not test_passed:
            defects.append({
                "rule": "Khoản 1 Điều 13 Nghị định 06/2021/NĐ-CP",
                "issue": f"Chưa có kết quả thí nghiệm đạt chuẩn cho hạng mục '{work_item}'.",
                "order": "DỪNG NGHIỆM THU NGAY LẬP TỨC. Tuyệt đối không cho phép thi công công đoạn tiếp theo."
            })
            compliance_checks.append({
                "check": "KẾT QUẢ THÍ NGHIỆM ĐẠT CHUẨN",
                "status": "FAIL",
                "details": "Chưa có kết quả hoặc kết quả không đạt"
            })
        else:
            compliance_checks.append({
                "check": "KẾT QUẢ THÍ NGHIỆM ĐẠT CHUẨN",
                "status": "PASS",
                "details": "Kết quả thí nghiệm hoàn toàn phù hợp quy chuẩn kỹ thuật"
            })

        # 2. Rà soát nhật ký thi công theo Thông tư 10/2021/TT-BXD
        if not log_updated:
            defects.append({
                "rule": "Thông tư 10/2021/TT-BXD (Quy định chi tiết về nhật ký thi công)",
                "issue": "Nhật ký thi công chưa được hoàn thiện và ký xác nhận của các bên liên quan.",
                "order": "Yêu cầu TVGS và Chỉ huy trưởng ký đóng dấu nhật ký trước khi ký Biên bản nghiệm thu."
            })
            compliance_checks.append({
                "check": "NHẬT KÝ THI CÔNG TT 10/2021",
                "status": "FAIL",
                "details": "Chưa ký nhật ký"
            })
        else:
            compliance_checks.append({
                "check": "NHẬT KÝ THI CÔNG TT 10/2021",
                "status": "PASS",
                "details": "Nhật ký thi công ghi chép đầy đủ đúng quy trình"
            })

        # 3. Rà soát mẫu dấu hoàn công 4 bên theo Phụ lục II Nghị định 06/2021/NĐ-CP
        missing_sigs = []
        for req_sig in cls.REQUIRED_SIGNATURES_ASBUILT:
            found = any(req_sig.lower() in s.lower() for s in collected_sigs)
            if not found:
                missing_sigs.append(req_sig)

        if missing_sigs:
            defects.append({
                "rule": "Phụ lục II Nghị định số 06/2021/NĐ-CP",
                "issue": f"Mẫu dấu hoàn công thiếu chữ ký hợp pháp của: {missing_sigs}.",
                "order": "Thu hồi bản vẽ để bổ sung đủ chữ ký chức danh và mộc pháp nhân."
            })
            compliance_checks.append({
                "check": "MẪU DẤU HOÀN CÔNG PHỤ LỤC II NĐ 06/2021",
                "status": "FAIL",
                "details": f"Thiếu {len(missing_sigs)} chữ ký bắt buộc"
            })
        else:
            compliance_checks.append({
                "check": "MẪU DẤU HOÀN CÔNG PHỤ LỤC II NĐ 06/2021",
                "status": "PASS",
                "details": "Đầy đủ 4 chữ ký hợp pháp theo quy định"
            })

        # 4. Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        is_blocked = len(defects) > 0
        gate_status = "BLOCKED_REVISE" if is_blocked else "APPROVED_FOR_TRANSFER"

        next_step = ""
        if is_blocked:
            next_step = f"CHẶN CHUYỂN BƯỚC THI CÔNG. Phát hiện {len(defects)} lỗi quy trình. Yêu cầu Kỹ sư Bùi Văn Nghiệm lập biên bản đình chỉ/khắc phục tại hiện trường."
        else:
            next_step = "BAN HÀNH LỆNH CHUYỂN BƯỚC THI CÔNG. Đủ điều kiện chuyển hồ sơ sang Ban Kiểm toán Thanh Quyết toán để làm căn cứ giải ngân Mẫu 08a."

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": "Nghị định 06/2021/NĐ-CP & Thông tư 10/2021/TT-BXD",
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
        
        # BƯỚC 1: Chuyên viên hiện trường thu thập dữ liệu & lập hồ sơ
        specialist_dossier = SiteQCSpecialistAgent.execute_field_inspection(
            work_item=work_item,
            inspection_date=inspection_date,
            test_results_passed=test_results_passed,
            logbook_updated=logbook_updated,
            asbuilt_stamp_signatures=asbuilt_stamp_signatures
        )

        # BƯỚC 2: Trưởng phòng rà soát quy trình, quy chuẩn NĐ 06/2021 & cấp lệnh chuyển bước
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
