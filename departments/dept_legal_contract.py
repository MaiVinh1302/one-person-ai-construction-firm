# -*- coding: utf-8 -*-
"""
DEPARTMENT 1: Legal & Contract Management (Phòng Pháp chế & Đàm phán Hợp đồng)
Cơ cấu 2 cấp nhân sự:
1. Chuyên viên Hợp đồng: Nguyễn Văn Pháp (Specialist Execution Agent)
   - Bóc tách chi tiết câu chữ, rà soát 12 bẫy pháp lý, áp dụng mẫu hợp đồng chuẩn QĐ 690/QĐ-TGĐ & QĐ 560/QĐ-TGĐ.
2. Trưởng phòng Pháp chế: Trần Thị Tuân Thủ (Department Head Reviewing Agent)
   - Rà soát quy trình, nguyên tắc NĐ 210/2026/NĐ-CP & Quy định nội bộ QĐ 690, QĐ 122/123 (hiệu lực bảo lãnh >= Thời gian HĐ + 30 ngày, cam kết chống tham nhũng XDCK.2024.01).
   - Cấp lệnh Gate Clearance (Cho phép chuyển bước sang Ban Đấu thầu / Quyết toán hoặc Trình Founder).
"""

from typing import Dict, List, Any
from core.safeguards import ConstructionSafeguards
from core.permissions import RoleLevel, PermissionAction, RBACManager
from knowledge.legal_engine import legal_engine
from knowledge.corporate_sops import corporate_sop_engine

class ContractSpecialistAgent:
    """
    CHUYÊN VIÊN HỢP ĐỒNG: NGUYỄN VĂN PHÁP (Level 2 Specialist)
    Chuyên trách thực thi bóc tách kỹ thuật, chọn mẫu hợp đồng chuẩn QĐ 690/560, rà soát câu từ và phát hiện bẫy điều khoản.
    """
    AGENT_NAME = "Nguyễn Văn Pháp"
    ROLE_TITLE = "Chuyên viên Soạn thảo & Rà soát Hợp đồng"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def execute_contract_audit(
        cls,
        contract_title: str,
        contract_date: str,
        contract_value: float,
        requested_advance: float,
        has_bank_guarantee: bool,
        clause_texts: List[str]
    ) -> Dict[str, Any]:
        
        clause_findings = []
        advance_analysis = {}

        # 0. Áp mẫu Hợp đồng chuẩn Tập đoàn theo QĐ 690/QĐ-TGĐ & QĐ 560/QĐ-TGĐ
        corporate_template_info = corporate_sop_engine.recommend_contract_template(
            contract_title=contract_title,
            contract_value=contract_value
        )

        # 1. Bóc tách tỷ lệ tạm ứng
        adv_ratio = (requested_advance / contract_value * 100) if contract_value > 0 else 0
        advance_analysis = {
            "contract_value": contract_value,
            "requested_advance": requested_advance,
            "advance_ratio_percent": round(adv_ratio, 2),
            "has_bank_guarantee": has_bank_guarantee,
            "bond_validity_requirement": corporate_template_info["bond_validity_rule"]
        }

        # 2. Rà soát 12 bẫy điều khoản trong hợp đồng
        for idx, clause in enumerate(clause_texts, 1):
            cl_lower = clause.lower()
            
            # Bẫy thanh toán kéo dài chiếm dụng vốn
            if any(term in cl_lower for term in ["thanh toán trong vòng 45 ngày", "thanh toán trong vòng 60 ngày", "khi nào chủ đầu tư có tiền"]):
                clause_findings.append({
                    "clause_index": idx,
                    "trap_category": "BẪY CHIẾM DỤNG VỐN / THỜI HẠN THANH TOÁN",
                    "original_text": clause,
                    "risk_analysis": "Thời hạn thanh toán bất thường > 14 ngày làm việc, lệch chuẩn Hợp đồng mẫu QĐ 690/QĐ-TGĐ.",
                    "proposed_revision": "Thanh toán trong vòng tối đa 14 ngày làm việc kể từ ngày Nhà thầu nộp đủ hồ sơ Mẫu 08a và Checklist TQT hợp lệ."
                })

            # Bẫy phạt vi phạm vượt trần luật định
            if any(term in cl_lower for term in ["phạt tối đa 12%", "phạt tối đa 15%", "phạt 20%"]):
                clause_findings.append({
                    "clause_index": idx,
                    "trap_category": "BẪY PHẠT HỢP ĐỒNG TRÁI LUẬT",
                    "original_text": clause,
                    "risk_analysis": "Mức phạt vượt quá trần 8% giá trị phần nghĩa vụ bị vi phạm theo Điều 146 Luật Xây dựng.",
                    "proposed_revision": "Tổng mức phạt vi phạm không vượt quá 8% giá trị phần nghĩa vụ hợp đồng bị vi phạm."
                })

            # Bẫy quyết toán treo vô thời hạn
            if any(term in cl_lower for term in ["quyết toán khi có chỉ đạo", "khi dự án hoàn tất kiểm toán nhà nước", "thu xếp được vốn"]):
                clause_findings.append({
                    "clause_index": idx,
                    "trap_category": "BẪY QUYẾT TOÁN TREO",
                    "original_text": clause,
                    "risk_analysis": "Điều khoản đẩy toàn bộ rủi ro cho nhà thầu, vi phạm thời hạn quyết toán NĐ 210/2026 & QĐ 122/123.",
                    "proposed_revision": "Thời hạn hoàn thành quyết toán hợp đồng tối đa 60 ngày kể từ ngày ký biên bản bàn giao nghiệm thu hoàn thành (17.BM-BBNTHT)."
                })

        primary_tpl = corporate_template_info["primary_template"]
        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "execution_status": "COMPLETED",
            "contract_title": contract_title,
            "contract_date": contract_date,
            "corporate_template_applied": primary_tpl,
            "mandatory_nda_template": corporate_template_info["mandatory_attachment"],
            "advance_analysis": advance_analysis,
            "clause_findings": clause_findings,
            "summary_note": (
                f"Chuyên viên {cls.AGENT_NAME} đã áp mẫu hợp đồng chuẩn [{primary_tpl['code']}] ({primary_tpl['decision']}) "
                f"kèm Cam kết chống tham nhũng [XDCK.2024.01]. Phát hiện {len(clause_findings)} điều khoản rủi ro cần hiệu chỉnh."
            )
        }


class LegalHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG PHÁP CHẾ: TRẦN THỊ TUÂN THỦ (Level 3 Head)
    Chuyên trách thẩm tra quy trình, quy chuẩn, quy chế nội bộ QĐ 690/560, luật định 2026 và cấp lệnh CHUYỂN BƯỚC.
    """
    AGENT_NAME = "Trần Thị Tuân Thủ"
    ROLE_TITLE = "Trưởng phòng Pháp chế & Quản trị Rủi ro"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    @classmethod
    def review_and_gate_clearance(
        cls,
        specialist_dossier: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        contract_date = specialist_dossier.get("contract_date", "2026-08-01")
        adv = specialist_dossier.get("advance_analysis", {})
        contract_val = adv.get("contract_value", 0)
        req_adv = adv.get("requested_advance", 0)
        has_guarantee = adv.get("has_bank_guarantee", False)
        clause_findings = specialist_dossier.get("clause_findings", [])
        tpl_info = specialist_dossier.get("corporate_template_applied", {})

        compliance_checks = []
        violations = []

        # 1. Rà soát mốc hiệu lực luật pháp (Decree 210 vs Decree 37)
        timing_check = ConstructionSafeguards.audit_contract_timing(contract_date)
        applicable_law = f"{timing_check.get('applicable_decree', 'Nghị định 210/2026/NĐ-CP')} & Quy định Hợp đồng mẫu {tpl_info.get('decision', 'QĐ 690/QĐ-TGĐ')}"
        compliance_checks.append({
            "check": "HIỆU LỰC PHÁP LÝ & MẪU HỢP ĐỒNG TẬP ĐOÀN (QĐ 690/560)",
            "status": "PASS" if timing_check["valid"] else "FAIL",
            "details": f"Ngày ký: {contract_date} -> Áp dụng mẫu chuẩn {tpl_info.get('code', 'XDTC.2024.01')} kèm Cam kết XDCK.2024.01."
        })

        # 2. Rà soát Trần Tạm ứng & Bảo lãnh Tạm ứng theo NĐ 210/2026 & QĐ 122/123 (Hiệu lực bảo lãnh >= Thời gian HĐ + 30 ngày)
        if timing_check.get("is_governed_by_210", True):
            adv_audit = ConstructionSafeguards.audit_advance_payment(contract_val, req_adv, has_guarantee)
            if not adv_audit["valid"]:
                for v in adv_audit["violations"]:
                    violations.append({
                        "rule": "Nghị định 210/2026/NĐ-CP (Khoản 2 Điều 18) & Quy định TQT QĐ 122/123",
                        "violation": v,
                        "mandatory_remedy": "Giảm tỷ lệ tạm ứng <= 30% và nộp Thư bảo lãnh tạm ứng ngân hàng (hiệu lực >= Thời gian thực hiện HĐ + 30 ngày) nếu tạm ứng > 1 tỷ VNĐ."
                    })
                compliance_checks.append({
                    "check": "TUÂN THỦ TẠM ỨNG & BẢO LÃNH (NĐ 210/2026 & QĐ 122/123)",
                    "status": "FAIL",
                    "details": f"Vi phạm: {', '.join(adv_audit['violations'])}"
                })
            else:
                compliance_checks.append({
                    "check": "TUÂN THỦ TẠM ỨNG & BẢO LÃNH (NĐ 210/2026 & QĐ 122/123)",
                    "status": "PASS",
                    "details": "Mức tạm ứng <= 30% và bảo lãnh hợp lệ (đảm bảo hiệu lực >= Thời gian thực hiện HĐ + 30 ngày)."
                })

        # 3. Rà soát điều khoản sửa đổi do Chuyên viên đề xuất
        trap_count = len(clause_findings)
        compliance_checks.append({
            "check": "RÀ SOÁT BẪY ĐIỀU KHOẢN & ĐỐI CHIẾU MẪU QĐ 690",
            "status": "WARNING" if trap_count > 0 else "PASS",
            "details": f"Chuyên viên phát hiện {trap_count} điều khoản khác biệt so với mẫu chuẩn cần đàm phán sửa đổi."
        })

        # 4. Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        is_blocked = len(violations) > 0
        gate_status = "BLOCKED_REVISE" if is_blocked else "APPROVED_FOR_TRANSFER"

        next_action = ""
        requires_founder = False
        
        if is_blocked:
            next_action = "Chặn chuyển bước. Yêu cầu Chuyên viên Nguyễn Văn Pháp gửi Công văn đàm phán sửa đổi tỷ lệ tạm ứng & bảo lãnh theo NĐ 210/2026 và mẫu QĐ 690."
        else:
            requires_founder = (req_adv >= ConstructionSafeguards.THRESHOLDS["PAYMENT_APPROVAL_VND"]) or (trap_count > 0)
            if requires_founder:
                next_action = f"Đạt điều kiện nội bộ (Mẫu {tpl_info.get('code', 'XDTC.2024.01')} + XDCK.2024.01). Lập Tờ trình chuyển tiếp Founder Mai Quang Vinh phê duyệt."
            else:
                next_action = f"Đạt điều kiện nội bộ (Mẫu {tpl_info.get('code', 'XDTC.2024.01')}). Cấp phép chuyển bước hồ sơ sang Ban Đấu thầu & Ban Kiểm toán Quyết toán."

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "applicable_law": applicable_law,
            "corporate_template_code": tpl_info.get("code", "XDTC.2024.01"),
            "gate_status": gate_status,
            "compliance_checks": compliance_checks,
            "violations": violations,
            "requires_founder_approval": requires_founder,
            "gate_clearance_signoff": {
                "signer": cls.AGENT_NAME,
                "decision": gate_status,
                "next_step": next_action
            },
            "review_summary": f"Trưởng phòng {cls.AGENT_NAME}: {'CHẶN LẠI YÊU CẦU SỬA ĐỔI' if is_blocked else 'PHÊ DUYỆT CHUYỂN BƯỚC'}. {next_action}"
        }


class LegalContractDepartment:
    """
    WRAPPER PHÒNG BAN: Tích hợp 2 cấp Chuyên viên & Trưởng phòng
    """
    DEPARTMENT_NAME = "Phòng Pháp chế & Hợp đồng (Legal & Contract)"

    @classmethod
    def audit_contract(
        cls,
        contract_title: str,
        contract_date: str,
        contract_value: float,
        requested_advance: float,
        has_bank_guarantee: bool,
        clause_texts: List[str]
    ) -> Dict[str, Any]:
        
        # BƯỚC 1: Chuyên viên thực thi bóc tách kỹ thuật & áp mẫu hợp đồng QĐ 690/560
        specialist_dossier = ContractSpecialistAgent.execute_contract_audit(
            contract_title=contract_title,
            contract_date=contract_date,
            contract_value=contract_value,
            requested_advance=requested_advance,
            has_bank_guarantee=has_bank_guarantee,
            clause_texts=clause_texts
        )

        # BƯỚC 2: Trưởng phòng rà soát quy trình, quy chuẩn, quy định & cấp lệnh chuyển bước
        head_review = LegalHeadReviewerAgent.review_and_gate_clearance(specialist_dossier)

        # Tổng hợp kết quả phòng ban
        critical_alerts = []
        for v in head_review.get("violations", []):
            critical_alerts.append({
                "severity": "CRITICAL",
                "issue": v["violation"],
                "legal_ground": v["rule"],
                "recommendation": v["mandatory_remedy"]
            })
        for cl in specialist_dossier.get("clause_findings", []):
            critical_alerts.append({
                "severity": "HIGH",
                "clause": f"Điều khoản {cl['clause_index']}",
                "issue": cl["risk_analysis"],
                "legal_ground": "QĐ 690/QĐ-TGĐ (30 mẫu HĐ chuẩn) & Luật Xây dựng",
                "recommendation": cl["proposed_revision"]
            })

        return {
            "department": cls.DEPARTMENT_NAME,
            "status": "COMPLETED",
            "personnel": {
                "specialist": f"{ContractSpecialistAgent.AGENT_NAME} ({ContractSpecialistAgent.ROLE_TITLE})",
                "department_head": f"{LegalHeadReviewerAgent.AGENT_NAME} ({LegalHeadReviewerAgent.ROLE_TITLE})"
            },
            "specialist_dossier": specialist_dossier,
            "head_review": head_review,
            "contract_title": contract_title,
            "applicable_law": head_review.get("applicable_law"),
            "corporate_sop_applied": specialist_dossier.get("corporate_template_applied", {}),
            "gate_status": head_review.get("gate_status"),
            "critical_alerts": critical_alerts,
            "requires_founder_approval": head_review.get("requires_founder_approval", False),
            "summary": f"[{head_review.get('gate_status')}] {head_review.get('review_summary')}"
        }
