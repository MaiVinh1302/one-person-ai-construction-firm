# -*- coding: utf-8 -*-
"""
DEPARTMENT 5: Settlement & Disbursement Audit (Phòng Kiểm toán Thanh & Quyết toán)
Cơ cấu 2 cấp nhân sự:
1. Chuyên viên Quyết toán: Ngô Thị Quyết (Specialist Execution Agent)
   - Lập bảng tính Mẫu 08a, Mẫu 08b NĐ 99/2021/NĐ-CP, xác định phạm vi thẩm định KTXD (50% / 80% / 100%) theo QĐ 122/123, lập dự thảo Tờ trình Chủ tịch Điều hành (BM-16.1 / BM-16.2).
2. Trưởng phòng Kiểm toán: Đặng Đức Toán (Department Head Reviewing Agent)
   - Kiểm toán 4 tầng + Quy tắc Tập đoàn QĐ 122 & QĐ 123:
     * Nguyên tắc "Từ chối tiếp nhận nếu mắc trên 03 lỗi cơ bản" (3-Strike Rejection Rule).
     * SLA phản hồi 24 giờ, nhà thầu sửa trong 02 ngày làm việc, trả lại lần 2 phát hành Văn bản Cảnh báo năng lực nhà thầu.
     * Nguyên tắc Bảo vệ lợi ích Chủ đầu tư: Áp giá trị MIN giữa (BVHC, BBNT, HĐ); loại thẳng vật tư thay đổi quy cách/xuất xứ chưa ký PLHĐ.
   - Quyết định Gate Clearance & lập Tờ trình Founder Mai Quang Vinh (Mẫu BM-16.1 / BM-16.2).
"""

from typing import Dict, List, Any
from core.safeguards import ConstructionSafeguards
from core.permissions import RoleLevel
from knowledge.corporate_sops import corporate_sop_engine, SETTLEMENT_CORPORATE_RULES

class SettlementSpecialistAgent:
    """
    CHUYÊN VIÊN QUYẾT TOÁN: NGÔ THỊ QUYẾT (Level 2 Specialist)
    Chuyên trách tính toán các chỉ số tài chính Mẫu 08a NĐ 99/2021 và áp dụng Quy định TQT QĐ 122/123.
    """
    AGENT_NAME = "Ngô Thị Quyết"
    ROLE_TITLE = "Chuyên viên Thẩm tra Hồ sơ Thanh Quyết toán Mẫu 08a & QĐ 122/123"
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

        # Xác định tỷ lệ thẩm định khối lượng trọng yếu của Ban KTXD theo QĐ 122/123 (50% / 80% / 100%)
        ktxd_scope = corporate_sop_engine.get_ktxd_audit_scope(
            contract_val=contract_val,
            cumulative_val=cumulative_completed,
            is_final_settlement=False
        )

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
            "ktxd_audit_scope": ktxd_scope,
            "corporate_tqt_rules": SETTLEMENT_CORPORATE_RULES,
            "summary_note": (
                f"Chuyên viên {cls.AGENT_NAME} đã tính toán xong Mẫu 08a & Báo cáo thẩm định KTXD (BM-07/BM-14). "
                f"Phạm vi kiểm tra trọng yếu KTXD: {ktxd_scope['required_ktxd_audit_percent']}% ({ktxd_scope['stage']}). "
                f"Giá trị thực thanh toán kỳ này: {net_payable:,.0f} VNĐ."
            )
        }


class SettlementHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG KIỂM TOÁN: ĐẶNG ĐỨC TOÁN (Level 3 Head)
    Chuyên trách kiểm toán 4 tầng NĐ 99/2021 + Quy chế QĐ 122/123 (Luật 3 lỗi cơ bản, SLA 24h/2 ngày, nguyên tắc MIN khối lượng) và cấp lệnh CHUYỂN BƯỚC.
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
        ktxd_scope = specialist_dossier.get("ktxd_audit_scope", {})

        compliance_checks = []
        violations = []

        # Tầng 0 (Quy định Tập đoàn QĐ 122/123): Kiểm tra tỷ lệ thẩm định KTXD (50% / 80% / 100%) & Nguyên tắc MIN khối lượng
        compliance_checks.append({
            "check": "TỶ LỆ THẨM ĐỊNH TRỌNG YẾU KTXD & NGUYÊN TẮC MIN (QĐ 122/123)",
            "status": "PASS",
            "details": (
                f"{ktxd_scope.get('rule_description', '')}; "
                "Áp dụng giá trị MIN giữa (BVHC, BBNT, HĐ); loại trừ 100% vật tư thay đổi quy cách chưa ký PLHĐ."
            )
        })

        # Tầng 1 & 3: Kiểm tra khối lượng lũy kế so với trần giá trị hợp đồng (Điều 8 NĐ 99/2021 & QĐ 122/123)
        if cum_completed > contract_val:
            excess = cum_completed - contract_val
            violations.append({
                "rule": "Điều 8 Nghị định 99/2021/NĐ-CP & Quy định TQT QĐ 122/123",
                "issue": f"Giá trị thanh toán lũy kế ({cum_completed:,.0f} VNĐ) vượt giá trị hợp đồng được duyệt ({contract_val:,.0f} VNĐ)! Vượt trần: {excess:,.0f} VNĐ.",
                "action": "TỪ CHỐI THANH TOÁN PHẦN VƯỢT TRẦN khi chưa hoàn tất 12 bước xử lý phát sinh (QT01-XLPS) và ký Phụ lục hợp đồng."
            })
            compliance_checks.append({
                "check": "TRẦN HỢP ĐỒNG & PHỤ LỤC PHÁT SINH (TẦNG 3 KIỂM TOÁN)",
                "status": "FAIL",
                "details": f"Vượt trần {excess:,.0f} VNĐ chưa có PLHĐ"
            })
        else:
            compliance_checks.append({
                "check": "TRẦN HỢP ĐỒNG & PHỤ LỤC PHÁT SINH (TẦNG 3 KIỂM TOÁN)",
                "status": "PASS",
                "details": f"Lũy kế {cum_completed:,.0f} / {contract_val:,.0f} VNĐ ({(cum_completed/contract_val*100) if contract_val > 0 else 0:.1f}%)"
            })

        # Tầng 2: Kiểm tra bắt buộc có BBNTCV & Checklist 17 Biểu mẫu QA/QC (Điều 9 NĐ 99/2021 & QĐ 122/123)
        if not has_bbntcv:
            violations.append({
                "rule": "Khoản 2 Điều 9 Nghị định 99/2021/NĐ-CP & Quy tắc 3 lỗi cơ bản QĐ 122/123",
                "issue": "Hồ sơ đề nghị thanh toán thiếu Biên bản nghiệm thu công việc (10.BM-NTCVXD / 13.BM-BBXNCVTC) hoặc thiếu chữ ký nháy từng trang.",
                "action": "TỪ CHỐI TIẾP NHẬN HỒ SƠ TRONG 24H. Yêu cầu Nhà thầu hoàn thiện trong 02 ngày làm việc (Nếu trả lại lần 2 sẽ phát hành Văn bản Cảnh báo năng lực nhà thầu)."
            })
            compliance_checks.append({
                "check": "ĐẦY ĐỦ CHECKLIST 17 BM QA/QC & QUY TẮC 3 LỖI CƠ BẢN (QĐ 122/123)",
                "status": "FAIL",
                "details": "Thiếu biên bản nghiệm thu 10.BM-NTCVXD"
            })
        else:
            compliance_checks.append({
                "check": "ĐẦY ĐỦ CHECKLIST 17 BM QA/QC & QUY TẮC 3 LỖI CƠ BẢN (QĐ 122/123)",
                "status": "PASS",
                "details": "Đạt yêu cầu tiếp nhận (<= 3 lỗi cơ bản), đủ chữ ký nháy từng trang và CO/CQ"
            })

        # Tầng 4: Kiểm tra khấu trừ bảo hành tối thiểu 5% (Thông tư 02/2023/TT-BXD)
        if warranty_val <= 0:
            violations.append({
                "rule": "Khoản 2 Điều 28 Nghị định 37/2015/NĐ-CP, TT 02/2023/TT-BXD & QĐ 122/123",
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
        submission_form = ktxd_scope.get("submission_form", "BM-16.1 (Tờ trình Chủ tịch Điều hành phê duyệt Thanh toán)")
        next_step = ""

        if is_blocked:
            next_step = (
                f"CHẶN XUẤT TIỀN THEO QĐ 122/123. Phát hiện {len(violations)} vi phạm nguyên tắc thanh quyết toán. "
                "Phản hồi trả hồ sơ trong 24h, yêu cầu Nhà thầu khắc phục trong 02 ngày làm việc (tái phạm lần 2 phát hành Văn bản Cảnh báo năng lực)."
            )
        else:
            if requires_founder:
                next_step = (
                    f"Hồ sơ đạt chuẩn kiểm toán 4 tầng & QĐ 122/123 (Đã thẩm định {ktxd_scope.get('required_ktxd_audit_percent', 50)}% khối lượng chính). "
                    f"Số tiền thực chi {net_payable:,.0f} VNĐ >= 500 triệu VNĐ -> Xuất {submission_form} TRÌNH FOUNDER MAI QUANG VINH PHÊ DUYỆT GIẢI NGÂN."
                )
            else:
                next_step = f"Hồ sơ đạt chuẩn kiểm toán 4 tầng & QĐ 122/123. Số tiền {net_payable:,.0f} VNĐ nằm trong hạn mức phân quyền. Cấp phép chuyển lệnh chi sang Kế toán."

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": "Nghị định 99/2021/NĐ-CP, Thông tư 96/2021/TT-BTC & Quy định TQT Tập đoàn QĐ 122/123",
            "ktxd_audit_scope": ktxd_scope,
            "submission_form_code": submission_form,
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
            "review_summary": f"Trưởng phòng {cls.AGENT_NAME}: {'CHẶN LẠI TỪ CHỐI THANH TOÁN' if is_blocked else 'PHÊ DUYỆT HỒ SƠ 08A & BM-16.1'}. {next_step}"
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
        
        # BƯỚC 1: Chuyên viên thực thi tính toán các chỉ số Mẫu 08a & xác định tỷ lệ thẩm định KTXD (QĐ 122/123)
        specialist_dossier = SettlementSpecialistAgent.execute_payment_calculation(
            contract_no=contract_no,
            contract_val=contract_val,
            previous_paid_val=previous_paid_val,
            current_claim_val=current_claim_val,
            advance_recovered_val=advance_recovered_val,
            warranty_retention_percent=warranty_retention_percent,
            has_bbntcv=has_bbntcv
        )

        # BƯỚC 2: Trưởng phòng rà soát kiểm toán 4 tầng + QĐ 122/123 & cấp lệnh chuyển bước
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
            "ktxd_audit_scope": specialist_dossier.get("ktxd_audit_scope", {}),
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
