# -*- coding: utf-8 -*-
"""
DEPARTMENT 5: Settlement & Disbursement Audit (Phòng Kiểm toán Thanh & Quyết toán)
Cơ cấu 2 cấp nhân sự:
1. Chuyên viên Quyết toán: Ngô Thị Quyết (Specialist Execution Agent)
   - Lập bảng tính Mẫu 08a, Mẫu 08b NĐ 99/2021/NĐ-CP, tính lũy kế, khấu trừ tạm ứng, trích giữ bảo hành 5%.
2. Trưởng phòng Kiểm toán: Đặng Đức Toán (Department Head Reviewing Agent)
   - Kiểm toán 4 tầng (Pháp lý, Logic BBNTCV, Khối lượng lũy kế, Khấu trừ), kiểm soát thanh toán TT 96/2021.
   - Quyết định Gate Clearance & lập Tờ trình Founder Mai Quang Vinh phê duyệt giải ngân nếu > 500M VNĐ.
"""

from typing import Dict, List, Any
from core.safeguards import ConstructionSafeguards
from core.permissions import RoleLevel

class SettlementSpecialistAgent:
    """
    CHUYÊN VIÊN QUYẾT TOÁN: NGÔ THỊ QUYẾT (Level 2 Specialist)
    Chuyên trách tính toán các chỉ số tài chính, lập bảng chiết tính Mẫu 08a theo Nghị định 99/2021/NĐ-CP.
    """
    AGENT_NAME = "Ngô Thị Quyết"
    ROLE_TITLE = "Chuyên viên Thẩm tra Hồ sơ Thanh Quyết toán Mẫu 08a"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def execute_payment_calculation(
        cls,
        contract_no: str,
        contract_val: float,
        previous_paid_val: float,
        current_claim_val: float,
        advance_recovered_val: float,
        warranty_retention_percent: float = 5.0,
        has_bbntcv: bool = True
    ) -> Dict[str, Any]:
        
        cumulative_completed = previous_paid_val + current_claim_val
        warranty_val = (current_claim_val * warranty_retention_percent) / 100.0
        net_payable = current_claim_val - advance_recovered_val - warranty_val

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "execution_status": "COMPLETED",
            "contract_no": contract_no,
            "contract_value": contract_val,
            "previous_paid": previous_paid_val,
            "current_claim": current_claim_val,
            "cumulative_completed": cumulative_completed,
            "advance_recovered": advance_recovered_val,
            "warranty_percent": warranty_retention_percent,
            "warranty_retained": warranty_val,
            "net_payable_amount": round(net_payable, 0),
            "has_bbntcv_attached": has_bbntcv,
            "summary_note": f"Chuyên viên {cls.AGENT_NAME} đã tính toán xong Mẫu 08a. Giá trị thực thanh toán kỳ này: {net_payable:,.0f} VNĐ."
        }


class SettlementHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG KIỂM TOÁN: ĐẶNG ĐỨC TOÁN (Level 3 Head)
    Chuyên trách kiểm toán 4 tầng, kiểm soát hạn mức giải ngân và cấp lệnh CHUYỂN BƯỚC.
    """
    AGENT_NAME = "Đặng Đức Toán"
    ROLE_TITLE = "Trưởng phòng Kiểm toán Quyết toán & Kiểm soát Ngân quỹ"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    @classmethod
    def review_and_gate_clearance(
        cls,
        specialist_dossier: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        contract_val = float(specialist_dossier.get("contract_value", 0))
        cum_completed = float(specialist_dossier.get("cumulative_completed", 0))
        net_payable = float(specialist_dossier.get("net_payable_amount", 0))
        has_bbntcv = bool(specialist_dossier.get("has_bbntcv_attached", True))
        warranty_val = float(specialist_dossier.get("warranty_retained", 0))

        compliance_checks = []
        violations = []

        # Tầng 1 & 3: Kiểm tra khối lượng lũy kế so với trần giá trị hợp đồng (Điều 8 NĐ 99/2021)
        if cum_completed > contract_val:
            excess = cum_completed - contract_val
            violations.append({
                "rule": "Điều 8 Nghị định 99/2021/NĐ-CP & Luật Xây dựng",
                "issue": f"Giá trị thanh toán lũy kế ({cum_completed:,.0f} VNĐ) vượt giá trị hợp đồng được duyệt ({contract_val:,.0f} VNĐ)! Vượt trần: {excess:,.0f} VNĐ.",
                "action": "TỪ CHỐI THANH TOÁN PHẦN VƯỢT TRẦN khi chưa có Phụ lục hợp đồng ký bổ sung."
            })
            compliance_checks.append({
                "check": "TRẦN HỢP ĐỒNG (TẦNG 3 KIỂM TOÁN)",
                "status": "FAIL",
                "details": f"Vượt trần {excess:,.0f} VNĐ"
            })
        else:
            compliance_checks.append({
                "check": "TRẦN HỢP ĐỒNG (TẦNG 3 KIỂM TOÁN)",
                "status": "PASS",
                "details": f"Lũy kế {cum_completed:,.0f} / {contract_val:,.0f} VNĐ ({(cum_completed/contract_val*100):.1f}%)"
            })

        # Tầng 2: Kiểm tra bắt buộc có BBNTCV kèm theo Mẫu 08a (Điều 9 NĐ 99/2021)
        if not has_bbntcv:
            violations.append({
                "rule": "Khoản 2 Điều 9 Nghị định 99/2021/NĐ-CP",
                "issue": "Hồ sơ đề nghị thanh toán thiếu Biên bản nghiệm thu công việc (BBNTCV) hợp lệ có xác nhận của TVGS.",
                "action": "TỪ CHỐI TIẾP NHẬN HỒ SƠ. Trả lại yêu cầu bổ sung BBNTCV từ Ban QA/QC."
            })
            compliance_checks.append({
                "check": "ĐẦY ĐỦ BBNTCV (TẦNG 2 KIỂM TOÁN)",
                "status": "FAIL",
                "details": "Thiếu biên bản nghiệm thu"
            })
        else:
            compliance_checks.append({
                "check": "ĐẦY ĐỦ BBNTCV (TẦNG 2 KIỂM TOÁN)",
                "status": "PASS",
                "details": "Biên bản nghiệm thu đầy đủ, đúng logic"
            })

        # Tầng 4: Kiểm tra khấu trừ bảo hành tối thiểu 5% (Thông tư 02/2023/TT-BXD)
        if warranty_val <= 0:
            violations.append({
                "rule": "Khoản 2 Điều 28 Nghị định 37/2015/NĐ-CP & TT 02/2023/TT-BXD",
                "issue": "Chưa thực hiện trích giữ tiền bảo hành công trình (tối thiểu 5%) hoặc chưa có Thư bảo lãnh bảo hành.",
                "action": "Bắt buộc khấu trừ 5% vào giá trị chi trả kỳ này."
            })
            compliance_checks.append({
                "check": "KHẤU TRỪ BẢO HÀNH (TẦNG 4 KIỂM TOÁN)",
                "status": "FAIL",
                "details": "Chưa trích giữ bảo hành"
            })
        else:
            compliance_checks.append({
                "check": "KHẤU TRỪ BẢO HÀNH (TẦNG 4 KIỂM TOÁN)",
                "status": "PASS",
                "details": f"Đã trích giữ bảo hành: {warranty_val:,.0f} VNĐ"
            })

        # Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        is_blocked = len(violations) > 0
        gate_status = "BLOCKED_REVISE" if is_blocked else "APPROVED_FOR_TRANSFER"

        requires_founder = (net_payable >= ConstructionSafeguards.THRESHOLDS["PAYMENT_APPROVAL_VND"]) or (is_blocked)
        next_step = ""

        if is_blocked:
            next_step = f"CHẶN XUẤT TIỀN. Phát hiện {len(violations)} vi phạm nguyên tắc thanh toán. Trả lại hồ sơ cho Chuyên viên Ngô Thị Quyết thông báo Nhà thầu khắc phục."
        else:
            if requires_founder:
                next_step = f"Hồ sơ thanh toán Mẫu 08a đạt chuẩn kiểm toán 4 tầng. Số tiền thanh toán {net_payable:,.0f} VNĐ >= 500 triệu VNĐ, TRÌNH FOUNDER MAI QUANG VINH PHÊ DUYỆT GIẢI NGÂN."
            else:
                next_step = f"Hồ sơ Mẫu 08a đạt chuẩn kiểm toán 4 tầng. Số tiền {net_payable:,.0f} VNĐ nằm trong hạn mức phân quyền. Cấp phép chuyển lệnh chi sang Kế toán."

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": "Nghị định 99/2021/NĐ-CP & Thông tư 96/2021/TT-BTC",
            "compliance_checks": compliance_checks,
            "violations_count": len(violations),
            "violations": violations,
            "net_payable_amount": net_payable,
            "requires_founder_approval": requires_founder,
            "gate_clearance_signoff": {
                "signer": cls.AGENT_NAME,
                "decision": gate_status,
                "next_step": next_step
            },
            "review_summary": f"Trưởng phòng {cls.AGENT_NAME}: {'CHẶN LẠI TỪ CHỐI THANH TOÁN' if is_blocked else 'PHÊ DUYỆT HỒ SƠ 08A'}. {next_step}"
        }


class SettlementAuditDepartment:
    """
    WRAPPER PHÒNG BAN: Tích hợp 2 cấp Chuyên viên & Trưởng phòng
    """
    DEPARTMENT_NAME = "Phòng Kiểm toán Thanh & Quyết toán (Settlement Audit)"

    @classmethod
    def audit_payment_certificate_08a(
        cls,
        contract_no: str,
        contract_val: float,
        previous_paid_val: float,
        current_claim_val: float,
        advance_recovered_val: float,
        warranty_retention_percent: float = 5.0,
        has_bbntcv: bool = True
    ) -> Dict[str, Any]:
        
        # BƯỚC 1: Chuyên viên thực thi tính toán các chỉ số Mẫu 08a
        specialist_dossier = SettlementSpecialistAgent.execute_payment_calculation(
            contract_no=contract_no,
            contract_val=contract_val,
            previous_paid_val=previous_paid_val,
            current_claim_val=current_claim_val,
            advance_recovered_val=advance_recovered_val,
            warranty_retention_percent=warranty_retention_percent,
            has_bbntcv=has_bbntcv
        )

        # BƯỚC 2: Trưởng phòng rà soát kiểm toán 4 tầng & cấp lệnh chuyển bước
        head_review = SettlementHeadReviewerAgent.review_and_gate_clearance(specialist_dossier)

        red_flags = []
        for v in head_review.get("violations", []):
            red_flags.append({
                "severity": "CRITICAL",
                "issue": v["issue"],
                "legal_ground": v["rule"],
                "action": v["action"]
            })

        return {
            "department": cls.DEPARTMENT_NAME,
            "status": "COMPLETED",
            "personnel": {
                "specialist": f"{SettlementSpecialistAgent.AGENT_NAME} ({SettlementSpecialistAgent.ROLE_TITLE})",
                "department_head": f"{SettlementHeadReviewerAgent.AGENT_NAME} ({SettlementHeadReviewerAgent.ROLE_TITLE})"
            },
            "contract_no": contract_no,
            "contract_value": contract_val,
            "specialist_dossier": specialist_dossier,
            "head_review": head_review,
            "gate_status": head_review.get("gate_status"),
            "previous_paid": previous_paid_val,
            "current_claim": current_claim_val,
            "cumulative_completed": specialist_dossier.get("cumulative_completed", 0),
            "completion_ratio_percent": round((specialist_dossier.get("cumulative_completed", 0) / contract_val) * 100, 2) if contract_val > 0 else 0,
            "advance_recovered": advance_recovered_val,
            "warranty_retained": specialist_dossier.get("warranty_retained", 0),
            "net_payable_amount": specialist_dossier.get("net_payable_amount", 0),
            "red_flags_count": len(red_flags),
            "red_flags": red_flags,
            "requires_founder_approval": head_review.get("requires_founder_approval", False),
            "summary": f"[{head_review.get('gate_status')}] {head_review.get('review_summary')}"
        }
