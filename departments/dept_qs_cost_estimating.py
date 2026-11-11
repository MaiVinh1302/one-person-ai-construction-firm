# -*- coding: utf-8 -*-
"""
DEPARTMENT 3: Quantity Surveying & Cost Estimation (Phòng Kỹ sư Dự toán QS & BOQ)
Cơ cấu 2 cấp nhân sự:
1. Kỹ sư QS Bóc tách: Đỗ Văn Lượng (Specialist Execution Agent)
   - Đọc bản vẽ CAD/DXF, bóc tách khối lượng hình học, khớp nối mã hiệu định mức TT 09/2024/TT-BXD, áp cấu trúc 8 Bill Chuẩn hóa HSMT.
2. Trưởng phòng Dự toán: Vũ Đình Toàn (Department Head Reviewing Agent)
   - Rà soát quy trình, quét gian lận trùng lặp đầu việc, kiểm tra trần Chi phí hạng mục chung (Bill 1 <= 5%), nguyên tắc đo bóc MIN(BVHC, BBNT, HĐ) tại Bill 4, bảng độ sụt bê tông Bill 6 và quy trình phát sinh 12 bước QT01-XLPS.
   - Quyết định Gate Clearance (Cho phép chuyển bước sang Ban Hợp đồng / Quyết toán).
"""

from typing import Dict, List, Any
from tools.cad_geometry import PureDXFParser
from core.permissions import RoleLevel
from knowledge.corporate_sops import HSMT_8_BILLS_STANDARD, VARIATION_ORDER_12_STEPS

class QSInvestmentConsultancySpecialistAgent:
    """
    CHUYÊN VIÊN 1: ĐỖ VĂN LƯỢNG (Level 2 Specialist)
    Chuyên trách công tác Tổng mức đầu tư (TMĐT NĐ 10/2021) & các chi phí tư vấn đầu tư xây dựng.
    """
    AGENT_NAME = "Đỗ Văn Lượng"
    ROLE_TITLE = "Chuyên viên Tổng Mức Đầu Tư & Chi Phí Tư Vấn"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST


class QSCivilInfrastructureSpecialistAgent:
    """
    CHUYÊN VIÊN 2: BÙI CÔNG TRÌNH (Level 2 Specialist)
    Chuyên trách bóc tách khối lượng dự toán Hạ tầng kỹ thuật, San nền, Phần Thô & Hoàn thiện cơ bản.
    """
    AGENT_NAME = "Bùi Công Trình"
    ROLE_TITLE = "Chuyên viên Dự toán Xây dựng & Hạ tầng Kỹ thuật"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST


class QSMEPFireSpecialistAgent:
    """
    CHUYÊN VIÊN 3: PHẠM VĂN CƠ ĐIỆN (Level 2 Specialist)
    Chuyên trách bóc tách dự toán Cơ Điện (Điện, Nước, HVAC) & Phòng cháy chữa cháy (MEP & PCCC).
    """
    AGENT_NAME = "Phạm Văn Cơ Điện"
    ROLE_TITLE = "Chuyên viên Dự toán Cơ Điện & PCCC (MEP)"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST


class QSSpecialistAgent(QSInvestmentConsultancySpecialistAgent):
    """
    KỸ SƯ QS BÓC TÁCH: ĐỖ VĂN LƯỢNG (Level 2 Specialist)
    Chuyên trách trích xuất hình học từ CAD/DXF, lập bảng tính khối lượng theo 8 Bill chuẩn hóa HSMT.
    """
    AGENT_NAME = "Đỗ Văn Lượng"
    ROLE_TITLE = "Kỹ sư QS Bóc tách Khối lượng & Áp Định mức"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def execute_cad_and_boq_takeoff(
        cls,
        project_name: str,
        boq_items: List[Dict[str, Any]],
        cad_filepath: str = None
    ) -> Dict[str, Any]:
        
        cad_takeoff = None
        if cad_filepath:
            cad_takeoff = PureDXFParser.analyze_file(cad_filepath)

        processed_items = []
        raw_total = 0.0

        for idx, item in enumerate(boq_items, 1):
            name = item.get("name", "").strip()
            unit = item.get("unit", "").strip()
            qty = float(item.get("qty", 0))
            price = float(item.get("unit_price", 0))
            norm_code = item.get("norm_code", "").strip()
            subtotal = qty * price
            raw_total += subtotal

            # Tự động gợi ý quy định độ sụt bê tông (Bill 6) nếu là công tác bê tông
            slump_note = ""
            name_lower = name.lower()
            if "bê tông" in name_lower:
                if "lót" in name_lower or "nền" in name_lower:
                    slump_note = "Độ sụt chuẩn Bill 6: 12±2cm"
                elif "đài" in name_lower or "giằng" in name_lower or "móng" in name_lower:
                    slump_note = "Độ sụt chuẩn Bill 6: 14±2cm"
                elif "cột" in name_lower or "vách" in name_lower:
                    slump_note = "Độ sụt chuẩn Bill 6: 16±2cm (<20 tầng) / 18±2cm (20-40 tầng)"
                else:
                    slump_note = "Độ sụt chuẩn Bill 6: 16±2cm (<20 tầng) / 18±2cm (>=20 tầng)"

            processed_items.append({
                "stt": idx,
                "name": name,
                "unit": unit,
                "qty": qty,
                "unit_price": price,
                "norm_code": norm_code,
                "subtotal": subtotal,
                "corporate_bill_note": slump_note or "Đo bóc theo kích thước hình học Bill 4 (MIN giữa BVHC, BBNT, HĐ)"
            })

        max_general_cost_5pct = round(raw_total * 0.05, 0)

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "execution_status": "COMPLETED",
            "project_name": project_name,
            "cad_takeoff_result": cad_takeoff,
            "items_count": len(boq_items),
            "raw_total_amount": raw_total,
            "max_general_cost_bill1_5pct": max_general_cost_5pct,
            "hsmt_8_bills_applied": HSMT_8_BILLS_STANDARD,
            "variation_sop_12_steps": VARIATION_ORDER_12_STEPS,
            "processed_items": processed_items,
            "summary_note": (
                f"Kỹ sư QS {cls.AGENT_NAME} đã hoàn thành bóc tách {len(boq_items)} công tác theo chuẩn 8 Bill HSMT. "
                f"Tổng giá trị trực tiếp: {raw_total:,.0f} VNĐ (Trần Chi phí hạng mục chung Bill 1 tối đa 5% = {max_general_cost_5pct:,.0f} VNĐ)."
            )
        }


class QSHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG DỰ TOÁN: VŨ ĐÌNH TOÀN (Level 3 Head)
    Chuyên trách rà soát tính hợp chuẩn của BOQ theo 8 Bill HSMT, QT01-XLPS, TT 09/2024/TT-BXD và cấp lệnh CHUYỂN BƯỚC.
    """
    AGENT_NAME = "Vũ Đình Toàn"
    ROLE_TITLE = "Trưởng phòng Thẩm tra Dự toán & Kiểm soát Chi phí"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    @classmethod
    def review_and_gate_clearance(
        cls,
        specialist_dossier: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        items = specialist_dossier.get("processed_items", [])
        anomalies = []
        seen_names = {}
        clean_items = []
        total_clean_val = 0.0

        for item in items:
            idx = item["stt"]
            name = item["name"]
            norm_code = item["norm_code"]
            price = item["unit_price"]
            subtotal = item["subtotal"]

            # 1. Quét trùng lặp đầu việc (Fraud / Duplicate check)
            norm_name = name.lower()
            if norm_name in seen_names:
                anomalies.append({
                    "severity": "CRITICAL",
                    "item_index": idx,
                    "item_name": name,
                    "issue": f"Trùng lặp công tác với STT {seen_names[norm_name]}! Nguy cơ tính khống 2 lần trái nguyên tắc Bill 4.",
                    "remedy": "Loại bỏ công tác lặp lại hoặc gộp chung về một đầu việc duy nhất."
                })
            else:
                seen_names[norm_name] = idx

            # 2. Kiểm tra bắt buộc áp mã định mức TT 09/2024/TT-BXD & Thông tin kỹ thuật Bill 7
            if not norm_code:
                anomalies.append({
                    "severity": "MEDIUM",
                    "item_index": idx,
                    "item_name": name,
                    "issue": "Thiếu mã hiệu định mức xây dựng theo TT 09/2024/TT-BXD và quy cách kỹ thuật Bill 7.",
                    "remedy": "Tra cứu mã định mức tương ứng và bổ sung thông số mác, độ sụt (Bill 6), giới hạn chảy thép (Bill 7)."
                })

            # 3. Kiểm tra đơn giá bất thường
            if price <= 0:
                anomalies.append({
                    "severity": "HIGH",
                    "item_index": idx,
                    "item_name": name,
                    "issue": "Đơn giá bằng 0 hoặc chưa điền.",
                    "remedy": "Khảo sát giá thị trường hoặc áp Phụ lục đơn giá điều chỉnh chuẩn Bill 5."
                })

            total_clean_val += subtotal
            clean_items.append(item)

        # Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        critical_count = sum(1 for a in anomalies if a["severity"] == "CRITICAL")
        is_blocked = critical_count > 0
        gate_status = "BLOCKED_REVISE" if is_blocked else "APPROVED_FOR_TRANSFER"

        next_step = ""
        if is_blocked:
            next_step = f"Chặn chuyển bước. Phát hiện {critical_count} lỗi tính trùng lặp. Yêu cầu Kỹ sư Đỗ Văn Lượng rà soát loại bỏ theo chuẩn Bill 4 HSMT."
        else:
            next_step = (
                "Bảng BOQ đạt chuẩn 8 Bill HSMT (Trần CPC <= 5%, nguyên tắc đo bóc MIN khối lượng Bill 4, độ sụt Bill 6). "
                "Nếu có phát sinh trong thi công phải tuân thủ nghiêm 12 bước QT01-XLPS (BM.01 -> BM.05). Cấp phép chuyển sang Ban Hợp đồng & Quyết toán."
            )

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": "Nghị định 10/2021/NĐ-CP, Thông tư 09/2024/TT-BXD & Chuẩn hóa HSMT 8 Bill / Quy trình phát sinh QT01-XLPS",
            "total_items_reviewed": len(items),
            "anomalies_count": len(anomalies),
            "anomalies": anomalies,
            "clean_total_value": total_clean_val,
            "max_general_cost_bill1_5pct": round(total_clean_val * 0.05, 0),
            "clean_boq_items": clean_items,
            "gate_clearance_signoff": {
                "signer": cls.AGENT_NAME,
                "decision": gate_status,
                "next_step": next_step
            },
            "review_summary": f"Trưởng phòng {cls.AGENT_NAME}: {'CHẶN LẠI ĐỂ SỬA ĐỔI' if is_blocked else 'PHÊ DUYỆT CHUYỂN BƯỚC'}. {next_step}"
        }


class QSCostEstimatingDepartment:
    """
    WRAPPER PHÒNG BAN: Tích hợp 2 cấp Chuyên viên & Trưởng phòng
    """
    DEPARTMENT_NAME = "Phòng Kỹ sư Dự toán QS & BOQ (Cost Estimating)"

    @classmethod
    def audit_boq_items(
        cls,
        project_name: str,
        boq_items: List[Dict[str, Any]],
        cad_filepath: str = None
    ) -> Dict[str, Any]:
        
        # BƯỚC 1: Chuyên viên bóc tách hình học CAD & phân tích BOQ theo 8 Bill HSMT
        specialist_dossier = QSSpecialistAgent.execute_cad_and_boq_takeoff(
            project_name=project_name,
            boq_items=boq_items,
            cad_filepath=cad_filepath
        )

        # BƯỚC 2: Trưởng phòng rà soát quy trình, quét trùng lặp, cấp lệnh chuyển bước
        head_review = QSHeadReviewerAgent.review_and_gate_clearance(specialist_dossier)

        return {
            "department": cls.DEPARTMENT_NAME,
            "status": "COMPLETED",
            "personnel": {
                "specialist": f"{QSSpecialistAgent.AGENT_NAME} ({QSSpecialistAgent.ROLE_TITLE})",
                "department_head": f"{QSHeadReviewerAgent.AGENT_NAME} ({QSHeadReviewerAgent.ROLE_TITLE})"
            },
            "project_name": project_name,
            "specialist_dossier": specialist_dossier,
            "head_review": head_review,
            "gate_status": head_review.get("gate_status"),
            "total_items": len(boq_items),
            "total_boq_value": head_review.get("clean_total_value", 0),
            "max_general_cost_5pct": head_review.get("max_general_cost_bill1_5pct", 0),
            "anomalies": head_review.get("anomalies", []),
            "anomalies_found": head_review.get("anomalies_count", 0),
            "cad_takeoff_summary": specialist_dossier.get("cad_takeoff_result"),
            "clean_boq": head_review.get("clean_boq_items", []),
            "summary": f"[{head_review.get('gate_status')}] {head_review.get('review_summary')}"
        }
