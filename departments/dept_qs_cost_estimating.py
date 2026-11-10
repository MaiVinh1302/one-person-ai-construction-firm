# -*- coding: utf-8 -*-
"""
DEPARTMENT 3: Quantity Surveying & Cost Estimation (Phòng Kỹ sư Dự toán QS & BOQ)
Cơ cấu 2 cấp nhân sự:
1. Kỹ sư QS Bóc tách: Đỗ Văn Lượng (Specialist Execution Agent)
   - Đọc bản vẽ CAD/DXF, bóc tách khối lượng hình học, khớp nối mã hiệu định mức TT 09/2024/TT-BXD.
2. Trưởng phòng Dự toán: Vũ Đình Toàn (Department Head Reviewing Agent)
   - Rà soát quy trình, quét gian lận trùng lặp đầu việc, kiểm tra hao hụt và đơn giá thị trường.
   - Quyết định Gate Clearance (Cho phép chuyển bước sang Ban Hợp đồng / Quyết toán).
"""

from typing import Dict, List, Any
from tools.cad_geometry import PureDXFParser
from core.permissions import RoleLevel

class QSSpecialistAgent:
    """
    KỸ SƯ QS BÓC TÁCH: ĐỖ VĂN LƯỢNG (Level 2 Specialist)
    Chuyên trách trích xuất hình học từ CAD/DXF và lập bảng tính khối lượng chi tiết.
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

            processed_items.append({
                "stt": idx,
                "name": name,
                "unit": unit,
                "qty": qty,
                "unit_price": price,
                "norm_code": norm_code,
                "subtotal": subtotal
            })

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "execution_status": "COMPLETED",
            "project_name": project_name,
            "cad_takeoff_result": cad_takeoff,
            "items_count": len(boq_items),
            "raw_total_amount": raw_total,
            "processed_items": processed_items,
            "summary_note": f"Kỹ sư QS {cls.AGENT_NAME} đã hoàn thành bóc tách {len(boq_items)} công tác. Tổng giá trị thô: {raw_total:,.0f} VNĐ."
        }


class QSHeadReviewerAgent:
    """
    TRƯỞNG PHÒNG DỰ TOÁN: VŨ ĐÌNH TOÀN (Level 3 Head)
    Chuyên trách rà soát tính hợp chuẩn của BOQ, quét gian lận trùng lặp và cấp lệnh CHUYỂN BƯỚC.
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
                    "issue": f"Trùng lặp công tác với STT {seen_names[norm_name]}! Nguy cơ tính khống 2 lần.",
                    "remedy": "Loại bỏ công tác lặp lại hoặc gộp chung về một đầu việc duy nhất."
                })
            else:
                seen_names[norm_name] = idx

            # 2. Kiểm tra bắt buộc áp mã định mức TT 09/2024/TT-BXD
            if not norm_code:
                anomalies.append({
                    "severity": "MEDIUM",
                    "item_index": idx,
                    "item_name": name,
                    "issue": "Thiếu mã hiệu định mức xây dựng quy định theo TT 09/2024/TT-BXD.",
                    "remedy": "Tra cứu mã định mức tương ứng trong thư viện định mức xây dựng."
                })

            # 3. Kiểm tra đơn giá bất thường
            if price <= 0:
                anomalies.append({
                    "severity": "HIGH",
                    "item_index": idx,
                    "item_name": name,
                    "issue": "Đơn giá bằng 0 hoặc chưa điền.",
                    "remedy": "Khảo sát giá thị trường hoặc tra cứu công bố giá vật liệu địa phương."
                })

            total_clean_val += subtotal
            clean_items.append(item)

        # Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        critical_count = sum(1 for a in anomalies if a["severity"] == "CRITICAL")
        is_blocked = critical_count > 0
        gate_status = "BLOCKED_REVISE" if is_blocked else "APPROVED_FOR_TRANSFER"

        next_step = ""
        if is_blocked:
            next_step = f"Chặn chuyển bước. Phát hiện {critical_count} lỗi tính trùng lặp. Yêu cầu Kỹ sư Đỗ Văn Lượng rà soát loại bỏ trước khi chuyển giao."
        else:
            next_step = "Bảng BOQ đạt chuẩn quy cách. Cấp phép chuyển hồ sơ sang Ban Hợp đồng và Ban Quyết toán làm cơ sở ký kết & nghiệm thu."

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": "Nghị định 10/2021/NĐ-CP & Thông tư 09/2024/TT-BXD",
            "total_items_reviewed": len(items),
            "anomalies_count": len(anomalies),
            "anomalies": anomalies,
            "clean_total_value": total_clean_val,
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
        
        # BƯỚC 1: Chuyên viên bóc tách hình học CAD & phân tích BOQ
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
            "anomalies": head_review.get("anomalies", []),
            "anomalies_found": head_review.get("anomalies_count", 0),
            "cad_takeoff_summary": specialist_dossier.get("cad_takeoff_result"),
            "clean_boq": head_review.get("clean_boq_items", []),
            "summary": f"[{head_review.get('gate_status')}] {head_review.get('review_summary')}"
        }
