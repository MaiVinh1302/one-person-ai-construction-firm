# -*- coding: utf-8 -*-
"""
PERMISSIONS: Role-Based Access Control (RBAC) & Human-in-the-Loop Hierarchy
Ma trận phân quyền 5 tầng kiểm soát vận hành cho công ty xây dựng 1 người:
- Tầng 1: CÔNG CỤ (Tool)
- Tầng 2: CHUYÊN VIÊN CHUYÊN MÔN (Specialist Execution Agent)
- Tầng 3: TRƯỞNG PHÒNG KIỂM DUYỆT (Department Head Reviewing Agent)
- Tầng 4: ĐIỀU PHỐI VIÊN AI (Multi-Agent Orchestrator)
- Tầng 5: FOUNDER / CEO DUY NHẤT (Human Founder - Cấp quyền tối cao)
"""

from enum import Enum
from typing import Dict, List, Any

class RoleLevel(Enum):
    LEVEL_1_TOOL = 1        # Công cụ thực thi đọc/ghi dữ liệu cơ bản (CAD, Excel, Word)
    LEVEL_2_SPECIALIST = 2  # Chuyên viên chuyên môn (Bóc tách, tính toán, soạn thảo dự thảo)
    LEVEL_3_HEAD = 3        # Trưởng phòng kiểm duyệt (Rà soát quy trình, nguyên tắc, quy định, cấp lệnh chuyển bước)
    LEVEL_4_ORCHESTRATOR = 4# AI Orchestrator (Điều phối liên phòng ban, tổng hợp hồ sơ toàn công ty)
    LEVEL_5_FOUNDER = 5     # Founder / CEO con người duy nhất (Phê duyệt tối cao, giải ngân, ký số pháp lý)

class PermissionAction(Enum):
    # Tầng 1: Tools
    READ_DRAWING = "read_drawing"
    READ_BOQ = "read_boq"
    
    # Tầng 2: Specialist Execution
    DRAFT_CONTRACT_CLAUSES = "draft_contract_clauses"
    EXTRACT_CAD_TAKEOFF = "extract_cad_takeoff"
    MATCH_COST_NORMS = "match_cost_norms"
    COLLECT_BIDDING_QUOTES = "collect_bidding_quotes"
    DRAFT_INSPECTION_RECORD = "draft_inspection_record"
    CALCULATE_PAYMENT_08A = "calculate_payment_08a"
    
    # Tầng 3: Department Head Review & Gate Clearance
    VERIFY_PROCEDURE_COMPLIANCE = "verify_procedure_compliance"
    VERIFY_LEGAL_RULES_2026 = "verify_legal_rules_2026"
    SIGN_GATE_TRANSFER_CLEARANCE = "sign_gate_transfer_clearance"
    REJECT_INTERNAL_DRAFT = "reject_internal_draft"
    
    # Tầng 4: Orchestrator
    ROUTE_CROSS_DEPARTMENT = "route_cross_department"
    ESCALATE_TO_FOUNDER = "escalate_to_founder"
    
    # Tầng 5: Human Founder Only
    APPROVE_PAYMENT_OVER_500M = "approve_payment_over_500m"
    AWARD_TENDER = "award_tender"
    REJECT_ACCEPTANCE = "reject_acceptance"
    SIGN_CONTRACT_ANNEX = "sign_contract_annex"
    DISBURSE_FUNDS = "disburse_funds"

class RBACManager:
    """
    Kiểm soát quyền hạn nghiêm ngặt:
    - Chuyên viên chỉ thực thi và lập dự thảo, KHÔNG được tự ý chuyển bước sang phòng ban khác.
    - Trưởng phòng bắt buộc phải rà soát quy trình, quy chuẩn, quy chế, nếu ĐẠT mới cấp lệnh chuyển bước (Gate Clearance).
    - Founder con người nắm giữ quyền phê duyệt ngân sách >500M, trao thầu, ký kết hợp đồng.
    """

    PERMISSION_MAP: Dict[PermissionAction, RoleLevel] = {
        PermissionAction.READ_DRAWING: RoleLevel.LEVEL_1_TOOL,
        PermissionAction.READ_BOQ: RoleLevel.LEVEL_1_TOOL,

        PermissionAction.DRAFT_CONTRACT_CLAUSES: RoleLevel.LEVEL_2_SPECIALIST,
        PermissionAction.EXTRACT_CAD_TAKEOFF: RoleLevel.LEVEL_2_SPECIALIST,
        PermissionAction.MATCH_COST_NORMS: RoleLevel.LEVEL_2_SPECIALIST,
        PermissionAction.COLLECT_BIDDING_QUOTES: RoleLevel.LEVEL_2_SPECIALIST,
        PermissionAction.DRAFT_INSPECTION_RECORD: RoleLevel.LEVEL_2_SPECIALIST,
        PermissionAction.CALCULATE_PAYMENT_08A: RoleLevel.LEVEL_2_SPECIALIST,

        PermissionAction.VERIFY_PROCEDURE_COMPLIANCE: RoleLevel.LEVEL_3_HEAD,
        PermissionAction.VERIFY_LEGAL_RULES_2026: RoleLevel.LEVEL_3_HEAD,
        PermissionAction.SIGN_GATE_TRANSFER_CLEARANCE: RoleLevel.LEVEL_3_HEAD,
        PermissionAction.REJECT_INTERNAL_DRAFT: RoleLevel.LEVEL_3_HEAD,

        PermissionAction.ROUTE_CROSS_DEPARTMENT: RoleLevel.LEVEL_4_ORCHESTRATOR,
        PermissionAction.ESCALATE_TO_FOUNDER: RoleLevel.LEVEL_4_ORCHESTRATOR,

        PermissionAction.APPROVE_PAYMENT_OVER_500M: RoleLevel.LEVEL_5_FOUNDER,
        PermissionAction.AWARD_TENDER: RoleLevel.LEVEL_5_FOUNDER,
        PermissionAction.REJECT_ACCEPTANCE: RoleLevel.LEVEL_5_FOUNDER,
        PermissionAction.SIGN_CONTRACT_ANNEX: RoleLevel.LEVEL_5_FOUNDER,
        PermissionAction.DISBURSE_FUNDS: RoleLevel.LEVEL_5_FOUNDER,
    }

    @classmethod
    def can_execute(cls, action: PermissionAction, user_role: RoleLevel) -> Dict[str, Any]:
        required_level = cls.PERMISSION_MAP.get(action, RoleLevel.LEVEL_5_FOUNDER)
        has_permission = user_role.value >= required_level.value

        return {
            "allowed": has_permission,
            "action": action.value,
            "current_role": user_role.name,
            "required_role": required_level.name,
            "requires_human_approval": required_level == RoleLevel.LEVEL_5_FOUNDER
        }

    @classmethod
    def get_approval_matrix(cls) -> List[Dict[str, Any]]:
        """Trả về toàn bộ ma trận phân quyền để hiển thị trên Dashboard"""
        matrix = []
        for action, level in cls.PERMISSION_MAP.items():
            matrix.append({
                "action": action.value,
                "required_level": level.name,
                "level_number": level.value,
                "is_founder_only": level == RoleLevel.LEVEL_5_FOUNDER
            })
        return matrix
