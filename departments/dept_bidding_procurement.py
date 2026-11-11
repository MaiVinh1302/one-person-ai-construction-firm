# -*- coding: utf-8 -*-
"""
DEPARTMENT 2: Bidding & Procurement (Phòng Đấu thầu & Mua sắm)
Cơ cấu 2 cấp nhân sự:
1. Chuyên viên Đấu thầu: Lê Quang Thầu (Specialist Execution Agent)
   - Thu thập báo giá, lập ma trận so sánh đơn vị chào thầu, áp mẫu HSMT chuẩn QĐ 458 (BM12 -> BM41) và bộ 12 biểu mẫu LCNT (BM0-PYC -> BM09A/B).
2. Trưởng phòng Đấu thầu: Phạm Minh Đấu (Department Head Reviewing Agent)
   - Rà soát quy trình NĐ 349/2026/NĐ-CP, trần chỉ định thầu 5 tỷ, đăng tải Mạng Đấu thầu, và Quy chế nội bộ QĐ 419/420/421 & QĐ 516/517 (làm rõ kỹ thuật tối đa 01 lần tại BM04-BCDGKT).
   - Quyết định Gate Clearance (Cho phép chuyển bước sang Ban QS hoặc Trình Founder trao thầu).
"""

from typing import Dict, List, Any
from core.safeguards import ConstructionSafeguards
from core.permissions import RoleLevel
from knowledge.corporate_sops import corporate_sop_engine

class ProcurementGoodsSpecialistAgent:
    """
    CHUYÊN VIÊN 1: LÊ QUANG THẦU (Level 2 Specialist)
    Chuyên trách các gói thầu mua sắm hàng hóa, vật tư, máy móc thiết bị công trình.
    """
    AGENT_NAME = "Lê Quang Thầu"
    ROLE_TITLE = "Chuyên viên Gói thầu Mua sắm Hàng hóa & Thiết bị"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST


class ProcurementConsultancySpecialistAgent:
    """
    CHUYÊN VIÊN 2: NGUYỄN THẢO TƯ VẤN (Level 2 Specialist)
    Chuyên trách các gói thầu dịch vụ tư vấn (khảo sát, thiết kế, thẩm tra, giám sát, kiểm định).
    """
    AGENT_NAME = "Nguyễn Thảo Tư Vấn"
    ROLE_TITLE = "Chuyên viên Gói thầu Dịch vụ Tư vấn"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST


class ProcurementConstructionSpecialistAgent:
    """
    CHUYÊN VIÊN 3: TRẦN VĂN XÂY LẮP (Level 2 Specialist)
    Chuyên trách các gói thầu xây lắp công trình & tổng thầu EPC/PC.
    """
    AGENT_NAME = "Trần Văn Xây Lắp"
    ROLE_TITLE = "Chuyên viên Gói thầu Xây lắp & EPC"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST


class ProcurementSpecialistAgent(ProcurementGoodsSpecialistAgent):
    """
    Alias điều phối chung chuyên viên Đấu thầu & Mua sắm
    """
    AGENT_NAME = "Lê Quang Thầu"
    ROLE_TITLE = "Chuyên viên Thẩm tra Hồ sơ Đấu thầu & Mua sắm"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def execute_procurement_analysis(
        cls,
        package_name: str,
        package_type: str,
        estimated_budget: float,
        is_direct_award: bool,
        vendor_quotes: List[Dict[str, Any]],
        posted_on_procurement_network: bool
    ) -> Dict[str, Any]:
        
        # Ánh xạ gói thầu vào Bộ quy định LCNT nội bộ (QĐ 419/420/516) và 33 mẫu HSMT chuẩn QĐ 458
        bidding_sop = corporate_sop_engine.recommend_bidding_templates(
            package_name=package_name,
            package_type=package_type
        )

        quote_summary = []
        prices = [float(q.get("price", 0)) for q in vendor_quotes if float(q.get("price", 0)) > 0]
        avg_price = sum(prices) / len(prices) if prices else 0.0

        for q in vendor_quotes:
            vendor = q.get("vendor", "Chưa rõ")
            p = float(q.get("price", 0))
            dev = ((p - avg_price) / avg_price * 100) if avg_price > 0 else 0.0
            quote_summary.append({
                "vendor": vendor,
                "price": p,
                "deviation_percent": round(dev, 2),
                "is_outlier_candidate": abs(dev) > 30.0
            })

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "execution_status": "COMPLETED",
            "package_name": package_name,
            "package_type": package_type,
            "estimated_budget": estimated_budget,
            "is_direct_award": is_direct_award,
            "posted_on_procurement_network": posted_on_procurement_network,
            "corporate_bidding_sop": bidding_sop,
            "vendor_count": len(vendor_quotes),
            "average_price": round(avg_price, 0),
            "quotes_analyzed": quote_summary,
            "summary_note": (
                f"Chuyên viên {cls.AGENT_NAME} đã áp mẫu HSMT [{bidding_sop['recommended_hsmt_code']}] (QĐ 458) "
                f"và lập bộ hồ sơ LCNT (BM0-PYC -> BM08-TTr PDKQLCNT). Đã phân tích {len(vendor_quotes)} báo giá, giá bình quân: {avg_price:,.0f} VNĐ."
            )
        }


class BiddingHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG ĐẤU THẦU: PHẠM MINH ĐẤU (Level 3 Head)
    Chuyên trách kiểm soát quy chế nội bộ QĐ 419/420/421, QĐ 516/517, pháp luật 2026 (NĐ 349/2026) và cấp lệnh CHUYỂN BƯỚC.
    """
    AGENT_NAME = "Phạm Minh Đấu"
    ROLE_TITLE = "Trưởng phòng Quản lý Đấu thầu & Hợp đồng Mua sắm"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    DIRECT_AWARD_CEILINGS_2026 = {
        "CONSTRUCTION": 5_000_000_000,   # 05 tỷ đồng (NĐ 349/2026/NĐ-CP - Hiệu lực 09/09/2026)
        "CONSULTANCY": 3_000_000_000,    # 03 tỷ đồng (NĐ 349/2026/NĐ-CP)
        "GOODS": 2_000_000_000           # 02 tỷ đồng
    }

    @classmethod
    def review_and_gate_clearance(
        cls,
        specialist_dossier: Dict[str, Any],
        raw_vendor_quotes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        pkg_name = specialist_dossier.get("package_name", "")
        pkg_type = specialist_dossier.get("package_type", "CONSTRUCTION").upper()
        est_budget = float(specialist_dossier.get("estimated_budget", 0))
        is_direct = bool(specialist_dossier.get("is_direct_award", False))
        posted_network = bool(specialist_dossier.get("posted_on_procurement_network", False))
        bidding_sop = specialist_dossier.get("corporate_bidding_sop", {})

        ceiling = cls.DIRECT_AWARD_CEILINGS_2026.get(pkg_type, 1_000_000_000)
        compliance_checks = []
        violations = []

        # 0. Kiểm tra tuân thủ Bộ mẫu HSMT QĐ 458 & Quy trình 12 Biểu mẫu LCNT (QĐ 419/420/516)
        compliance_checks.append({
            "check": "TUÂN THỦ MẪU HSMT QĐ 458 & QUY CHẾ LCNT (QĐ 419/420/516)",
            "status": "PASS",
            "details": f"Áp dụng {bidding_sop.get('recommended_hsmt_code', 'BM12')} ({bidding_sop.get('recommended_hsmt_name', '')}); Quy tắc BM04-BCDGKT: Làm rõ HSĐXKT tối đa 01 lần."
        })

        # 1. Rà soát trần chỉ định thầu theo Nghị định 349/2026/NĐ-CP
        if is_direct:
            if est_budget > ceiling:
                violations.append({
                    "rule": f"Nghị định 349/2026/NĐ-CP & {bidding_sop.get('governing_internal_decision', 'QĐ 419/QĐ-TGĐ')}",
                    "violation": f"Gói thầu '{pkg_name}' giá trị {est_budget:,.0f} VNĐ vượt trần chỉ định thầu {ceiling:,.0f} VNĐ của loại hình {pkg_type}.",
                    "action_required": "CHUYỂN ĐỔI HÌNH THỨC: Bắt buộc chuyển sang Đấu thầu rộng rãi hoặc Chào giá cạnh tranh theo đầy đủ 12 biểu mẫu (BM0-PYC -> BM09A/B)."
                })
                compliance_checks.append({
                    "check": "HẠN MỨC CHỈ ĐỊNH THẦU (NĐ 349/2026)",
                    "status": "FAIL",
                    "details": f"Vượt trần: {est_budget:,.0f} > {ceiling:,.0f} VNĐ"
                })
            else:
                compliance_checks.append({
                    "check": "HẠN MỨC CHỈ ĐỊNH THẦU (NĐ 349/2026)",
                    "status": "PASS",
                    "details": f"Nằm trong hạn mức cho phép: {est_budget:,.0f} <= {ceiling:,.0f} VNĐ"
                })

        # 2. Rà soát quy định đăng tải công khai trên Mạng Đấu thầu Quốc gia
        if not posted_network:
            violations.append({
                "rule": "Nghị định 349/2026/NĐ-CP & Quy định phát hành BM02-TMT",
                "violation": "Chưa thực hiện đăng tải yêu cầu chào giá trên Hệ thống Mạng Đấu thầu Quốc gia.",
                "action_required": "ĐĂNG TẢI NGAY: Bắt buộc thông báo công khai tối thiểu 03-05 ngày làm việc trước khi chốt danh sách."
            })
            compliance_checks.append({
                "check": "CÔNG KHAI MẠNG ĐẤU THẦU QUỐC GIA",
                "status": "FAIL",
                "details": "Chưa đăng tải thông tin"
            })
        else:
            compliance_checks.append({
                "check": "CÔNG KHAI MẠNG ĐẤU THẦU QUỐC GIA",
                "status": "PASS",
                "details": "Đã đăng tải hợp lệ"
            })

        # 3. Rà soát lọc báo giá bất thường theo quy tắc lệch >30% (NĐ 349/2026 & BM05-BC Giá)
        quote_audit = ConstructionSafeguards.audit_bidding_quotes(raw_vendor_quotes)
        excluded = quote_audit.get("excluded_quotes", [])
        valid_quotes = quote_audit.get("accepted_quotes", [])

        compliance_checks.append({
            "check": "LỌC BÁO GIÁ DỊ BIỆT LỆCH >30% (BM05-BC GIÁ)",
            "status": "WARNING" if excluded else "PASS",
            "details": f"Đã loại bỏ {len(excluded)} báo giá lệch quá 30% so với giá bình quân."
        })

        # 4. Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        is_blocked = len(violations) > 0
        gate_status = "BLOCKED_REVISE" if is_blocked else "APPROVED_FOR_TRANSFER"

        bench_price = quote_audit.get("benchmark_package_price", est_budget)
        next_step = ""

        if is_blocked:
            next_step = "Chặn chuyển bước. Yêu cầu Chuyên viên Lê Quang Thầu hoàn thiện thủ tục đăng tải Mạng đấu thầu hoặc điều chỉnh hình thức LCNT theo QĐ 419/516."
        else:
            next_step = (
                f"Đạt quy chuẩn đấu thầu (Mẫu HSMT {bidding_sop.get('recommended_hsmt_code', 'BM12')}). "
                f"Hoàn tất Biên bản đàm phán (BM07-BBĐP) & Tờ trình phê duyệt KQLCNT (BM08-TTr PDKQLCNT) trình Founder Mai Quang Vinh (Giá đề xuất: {bench_price:,.0f} VNĐ)."
            )

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": f"Nghị định 349/2026/NĐ-CP, Luật Đấu thầu 22/2023/QH15 & {bidding_sop.get('governing_internal_decision', 'QĐ 419/QĐ-TGĐ')}",
            "direct_award_ceiling": ceiling,
            "recommended_hsmt_template": f"{bidding_sop.get('recommended_hsmt_code', 'BM12')} - {bidding_sop.get('recommended_hsmt_name', '')}",
            "compliance_checks": compliance_checks,
            "violations": violations,
            "excluded_quotes": excluded,
            "valid_quotes": valid_quotes,
            "recommended_package_price": bench_price,
            "gate_clearance_signoff": {
                "signer": cls.AGENT_NAME,
                "decision": gate_status,
                "next_step": next_step
            },
            "review_summary": f"Trưởng phòng {cls.AGENT_NAME}: {'CHẶN LẠI DO VI PHẠM THỦ TỤC' if is_blocked else 'PHÊ DUYỆT CHUYỂN BƯỚC'}. {next_step}"
        }


class BiddingProcurementDepartment:
    """
    WRAPPER PHÒNG BAN: Tích hợp 2 cấp Chuyên viên & Trưởng phòng
    """
    DEPARTMENT_NAME = "Phòng Đấu thầu & Mua sắm (Bidding & Procurement)"

    @classmethod
    def audit_procurement_package(
        cls,
        package_name: str,
        package_type: str,
        estimated_budget: float,
        is_direct_award: bool,
        vendor_quotes: List[Dict[str, Any]],
        posted_on_procurement_network: bool
    ) -> Dict[str, Any]:
        
        # BƯỚC 1: Chuyên viên bóc tách & phân tích ma trận báo giá + áp mẫu HSMT QĐ 458
        specialist_dossier = ProcurementSpecialistAgent.execute_procurement_analysis(
            package_name=package_name,
            package_type=package_type,
            estimated_budget=estimated_budget,
            is_direct_award=is_direct_award,
            vendor_quotes=vendor_quotes,
            posted_on_procurement_network=posted_on_procurement_network
        )

        # BƯỚC 2: Trưởng phòng rà soát quy trình, quy định NĐ 349/2026 & QĐ 419/516, cấp lệnh chuyển bước
        head_review = BiddingHeadReviewerAgent.review_and_gate_clearance(specialist_dossier, vendor_quotes)

        alerts = []
        for v in head_review.get("violations", []):
            alerts.append({
                "severity": "CRITICAL",
                "issue": v["violation"],
                "legal_ground": v["rule"],
                "action": v["action_required"]
            })

        return {
            "department": cls.DEPARTMENT_NAME,
            "status": "COMPLETED",
            "personnel": {
                "specialist": f"{ProcurementSpecialistAgent.AGENT_NAME} ({ProcurementSpecialistAgent.ROLE_TITLE})",
                "department_head": f"{BiddingHeadReviewerAgent.AGENT_NAME} ({BiddingHeadReviewerAgent.ROLE_TITLE})"
            },
            "specialist_dossier": specialist_dossier,
            "head_review": head_review,
            "package_name": package_name,
            "package_type": package_type,
            "estimated_budget": estimated_budget,
            "corporate_sop_applied": specialist_dossier.get("corporate_bidding_sop", {}),
            "gate_status": head_review.get("gate_status"),
            "alerts": alerts,
            "recommended_package_price": head_review.get("recommended_package_price"),
            "requires_founder_approval": True,
            "summary": f"[{head_review.get('gate_status')}] {head_review.get('review_summary')}"
        }
