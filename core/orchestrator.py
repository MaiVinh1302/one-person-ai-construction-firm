# -*- coding: utf-8 -*-
"""
CORE ORCHESTRATOR: Multi-Agent Executive Controller & StateGraph Engine
Điều phối 5 phòng ban ảo, mỗi phòng ban gồm:
- 01 Chuyên viên chuyên môn thực thi (Specialist Execution Agent)
- 01 Trưởng phòng kiểm duyệt quy trình, nguyên tắc, quy chuẩn (Department Head Reviewing Agent)
Tích hợp:
- Báo cáo thẩm tra riêng biệt từng phòng ban (Standalone Department Report)
- Báo cáo tổng hợp chuyên đề theo yêu cầu (Modular Multi-Workflow Report)
- Bộ bản báo cáo tổng thể toàn diện của công ty (Master Executive Dossier)
Quản lý hàng đợi phê duyệt Founder Mai Quang Vinh (Human-in-the-Loop).
"""

from typing import Dict, List, Any, Optional
from core.permissions import RoleLevel, PermissionAction, RBACManager
from core.safeguards import ConstructionSafeguards
from departments.dept_legal_contract import LegalContractDepartment, ContractSpecialistAgent, LegalHeadReviewerAgent
from departments.dept_bidding_procurement import (
    BiddingProcurementDepartment,
    ProcurementSpecialistAgent,
    ProcurementGoodsSpecialistAgent,
    ProcurementConsultancySpecialistAgent,
    ProcurementConstructionSpecialistAgent,
    BiddingHeadReviewerAgent
)
from departments.dept_qs_cost_estimating import (
    QSCostEstimatingDepartment,
    QSSpecialistAgent,
    QSInvestmentConsultancySpecialistAgent,
    QSCivilInfrastructureSpecialistAgent,
    QSMEPFireSpecialistAgent,
    QSHeadReviewerAgent
)
from departments.dept_qa_qc_site import (
    QAQCSiteDepartment,
    SiteQCSpecialistAgent,
    QASystemSpecialistAgent,
    QCSiteInspectionSpecialistAgent,
    HSESafetySpecialistAgent,
    QAQCHeadReviewerAgent
)
from departments.dept_settlement_audit import SettlementAuditDepartment, SettlementSpecialistAgent, SettlementHeadReviewerAgent
from departments.dept_marketing_media import MarketingMediaDepartment, ContentSpecialistAgent, VideoSpecialistAgent, MarketingHeadReviewerAgent
from core.reporting_engine import reporting_engine

class ConstructionCompanyOrchestrator:
    def __init__(self, founder_name: str = "Mai Quang Vinh"):
        self.founder_name = founder_name
        self.pending_approvals = []
        self.history_records = []
        self.gate_transfer_log = []
        self.latest_dept_results = {}
        self.generated_reports = []
        self.assigned_tasks = []

    def get_firm_roster(self) -> List[Dict[str, Any]]:
        """
        Danh bạ tổ chức công ty xây dựng 1 người: 5 phòng ban, mỗi phòng 2 nhân sự
        """
        return [
            {
                "id": "DEPT_LEGAL",
                "department_name": "Phòng Pháp chế & Đàm phán Hợp đồng",
                "code": "LEGAL",
                "corporate_sop": "QĐ 690/QĐ-TGĐ (30 mẫu HĐ XD/TV) & QĐ 560/QĐ-TGĐ (14 mẫu HĐ Cung ứng)",
                "specialist": {
                    "name": ContractSpecialistAgent.AGENT_NAME,
                    "title": ContractSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Áp mẫu HĐ chuẩn (XDTC.2024.01/02/03), kèm Cam kết chống tham nhũng XDCK.2024.01, phát hiện 12 bẫy điều khoản."
                },
                "head": {
                    "name": LegalHeadReviewerAgent.AGENT_NAME,
                    "title": LegalHeadReviewerAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_3_HEAD.name,
                    "mission": "Rà soát NĐ 210/2026/NĐ-CP (trần 30% tạm ứng, bảo lãnh >1 tỷ) & QĐ 122/123 (hiệu lực bảo lãnh >= Thời gian HĐ + 30 ngày)."
                }
            },
            {
                "id": "DEPT_BIDDING",
                "department_name": "Ban Quản lý Đấu thầu & Mua sắm",
                "code": "BIDDING",
                "corporate_sop": "QĐ 419/420/421, QĐ 516/517 (12 BM LCNT) & QĐ 458 (33 mẫu HSMT chuẩn)",
                "specialist_goods": {
                    "name": ProcurementGoodsSpecialistAgent.AGENT_NAME,
                    "title": ProcurementGoodsSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách các gói thầu mua sắm hàng hóa, vật tư, máy móc thiết bị, phân tích độ lệch giá chào thầu >30%."
                },
                "specialist_consultancy": {
                    "name": ProcurementConsultancySpecialistAgent.AGENT_NAME,
                    "title": ProcurementConsultancySpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách các gói thầu dịch vụ tư vấn (khảo sát, thiết kế, thẩm tra, giám sát, kiểm định, đánh giá tác động)."
                },
                "specialist_construction": {
                    "name": ProcurementConstructionSpecialistAgent.AGENT_NAME,
                    "title": ProcurementConstructionSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách các gói thầu xây lắp công trình, tổng thầu EPC/PC, đánh giá năng lực kinh nghiệm kỹ thuật nhà thầu."
                },
                "specialist": {
                    "name": f"{ProcurementGoodsSpecialistAgent.AGENT_NAME}, {ProcurementConsultancySpecialistAgent.AGENT_NAME}, {ProcurementConstructionSpecialistAgent.AGENT_NAME}",
                    "title": "Tổ Chuyên viên Đấu thầu & Mua sắm (Hàng hóa, Tư vấn, Xây lắp)",
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Lập 12 biểu mẫu LCNT (BM0-PYC -> BM08), áp 33 mẫu HSMT chuẩn QĐ 458, phân tích ma trận so sánh giá & làm rõ kỹ thuật."
                },
                "head": {
                    "name": BiddingHeadReviewerAgent.AGENT_NAME,
                    "title": BiddingHeadReviewerAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_3_HEAD.name,
                    "mission": "Rà soát trần chỉ định thầu 5 tỷ NĐ 349/2026, quy tắc làm rõ kỹ thuật tối đa 01 lần (BM04-BCDGKT), lọc giá lệch >30%."
                }
            },
            {
                "id": "DEPT_QS",
                "department_name": "Ban Dự toán QS & BOQ",
                "code": "QS_BOQ",
                "corporate_sop": "Chuẩn hóa HSMT 8 Bill (Trần CPC 5%, Độ sụt Bill 6) & Quy trình Phát sinh 12 bước QT01-XLPS",
                "specialist_investment": {
                    "name": QSInvestmentConsultancySpecialistAgent.AGENT_NAME,
                    "title": QSInvestmentConsultancySpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách lập và thẩm tra Tổng mức đầu tư (TMĐT NĐ 10/2021), suất vốn đầu tư, chi phí QLDA & các gói chi phí tư vấn."
                },
                "specialist_civil": {
                    "name": QSCivilInfrastructureSpecialistAgent.AGENT_NAME,
                    "title": QSCivilInfrastructureSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách bóc tách khối lượng CAD/DXF hạ tầng kỹ thuật, san nền, cọc móng, kết cấu thô & hoàn thiện cơ bản theo 8 Bill."
                },
                "specialist_mep": {
                    "name": QSMEPFireSpecialistAgent.AGENT_NAME,
                    "title": QSMEPFireSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách bóc tách dự toán Cơ Điện (Điện, Nước, HVAC, BMS) & Phòng cháy chữa cháy (PCCC) theo quy chuẩn QCVN 06:2022."
                },
                "specialist": {
                    "name": f"{QSInvestmentConsultancySpecialistAgent.AGENT_NAME}, {QSCivilInfrastructureSpecialistAgent.AGENT_NAME}, {QSMEPFireSpecialistAgent.AGENT_NAME}",
                    "title": "Tổ Kỹ sư QS & BOQ (Tổng mức đầu tư, Xây dựng hạ tầng, MEP & PCCC)",
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Bóc tách CAD/DXF, áp định mức TT 09/2024/TT-BXD, kiểm soát cấu trúc 8 Bill HSMT và bảng độ sụt BTTP (Bill 6)."
                },
                "head": {
                    "name": QSHeadReviewerAgent.AGENT_NAME,
                    "title": QSHeadReviewerAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_3_HEAD.name,
                    "mission": "Kiểm soát trần CPC <= 5% (Bill 2), nguyên tắc MIN(BVHC, BBNT, HĐ) tại Bill 4 và quy trình phát sinh 12 bước QT01-XLPS."
                }
            },
            {
                "id": "DEPT_QAQC",
                "department_name": "Ban Quản lý Chất lượng QA/QC",
                "code": "QAQC",
                "corporate_sop": "Bộ 17 Biểu mẫu Checklist Hồ sơ Chất lượng (1.BM-PD NTP -> 17.BM-BBNTHT) & Bill 8 HSMT",
                "specialist_qa": {
                    "name": QASystemSpecialistAgent.AGENT_NAME,
                    "title": QASystemSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách Đảm bảo chất lượng QA: Quy trình QLCL, kiểm soát NTP/NCC (1.BM), phòng LAS-XD (4.BM) & bản vẽ Shopdrawing Bill 8."
                },
                "specialist_qc": {
                    "name": QCSiteInspectionSpecialistAgent.AGENT_NAME,
                    "title": QCSiteInspectionSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách Kiểm soát chất lượng QC: Giám sát hiện trường, nghiệm thu vật liệu (7-8.BM), nén mẫu R28 (12.BM), BBNTCV & Nhật ký (15.BM)."
                },
                "specialist_hse": {
                    "name": HSESafetySpecialistAgent.AGENT_NAME,
                    "title": HSESafetySpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Chuyên trách An toàn lao động, Vệ sinh môi trường (HSE) & PCCC công trường: Nhật ký ATLĐ (16.BM), kiểm định máy móc, an toàn giàn giáo."
                },
                "specialist": {
                    "name": f"{QASystemSpecialistAgent.AGENT_NAME}, {QCSiteInspectionSpecialistAgent.AGENT_NAME}, {HSESafetySpecialistAgent.AGENT_NAME}",
                    "title": "Tổ Kỹ sư QA/QC & An toàn Công trình (QA Hệ thống, QC Hiện trường, HSE An toàn)",
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Kiểm tra phê duyệt NTP/NCC/LAS-XD (1->4.BM), nghiệm thu vật liệu (7-8.BM), công việc (9-10.BM) & nhật ký ATLĐ (16.BM)."
                },
                "head": {
                    "name": QAQCHeadReviewerAgent.AGENT_NAME,
                    "title": QAQCHeadReviewerAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_3_HEAD.name,
                    "mission": "Rà soát Điều 13 NĐ 06/2021, mẫu dấu hoàn công 4 bên Phụ lục II, thẩm quyền ký Shopdrawing (Bill 8), cấp Lệnh Chuyển bước."
                }
            },
            {
                "id": "DEPT_SETTLEMENT",
                "department_name": "Phòng Kiểm toán Thanh & Quyết toán",
                "code": "SETTLEMENT",
                "corporate_sop": "Quy định TQT QĐ 122 & QĐ 123 (Luật 3 lỗi cơ bản, Thẩm định KTXD 50%/80%/100%, Tờ trình BM-16.1/16.2)",
                "specialist": {
                    "name": SettlementSpecialistAgent.AGENT_NAME,
                    "title": SettlementSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Lập bảng Mẫu 08a/08b NĐ 99/2021, xác định tỷ lệ thẩm định KTXD (50%/80%/100%), soạn Tờ trình CTĐH (BM-16.1/16.2)."
                },
                "head": {
                    "name": SettlementHeadReviewerAgent.AGENT_NAME,
                    "title": SettlementHeadReviewerAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_3_HEAD.name,
                    "mission": "Kiểm toán 4 tầng + Quy tắc 3 lỗi từ chối trong 24h (QĐ 122/123), áp nguyên tắc giá trị MIN có lợi cho CĐT, trình Founder giải ngân."
                }
            },
            {
                "id": "DEPT_MARKETING",
                "department_name": "Ban Marketing & Truyền Thông",
                "code": "MARKETING",
                "corporate_sop": "Quy chuẩn Nhận diện Thương hiệu T&T & Chiến lược Truyền thông Đa Kênh Xây dựng 2026",
                "specialist_content": {
                    "name": ContentSpecialistAgent.AGENT_NAME,
                    "title": ContentSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Sáng tạo bài viết PR báo chí, bài đăng mạng xã hội (Facebook, LinkedIn), lan tỏa hình ảnh uy tín doanh nghiệp."
                },
                "specialist_video": {
                    "name": VideoSpecialistAgent.AGENT_NAME,
                    "title": VideoSpecialistAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Lập kịch bản phân cảnh (Storyboard), thiết kế video quảng cáo năng lực, video ngắn TikTok/Reels/Shorts."
                },
                "specialist": {
                    "name": f"{ContentSpecialistAgent.AGENT_NAME} & {VideoSpecialistAgent.AGENT_NAME}",
                    "title": "Chuyên viên Sáng tạo Nội dung & Sản xuất Video Media",
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Sáng tạo bài viết PR, kịch bản phân cảnh Storyboard và sản xuất video quảng bá hình ảnh dự án & công ty."
                },
                "head": {
                    "name": MarketingHeadReviewerAgent.AGENT_NAME,
                    "title": MarketingHeadReviewerAgent.ROLE_TITLE,
                    "level": RoleLevel.LEVEL_3_HEAD.name,
                    "mission": "Thẩm định thông điệp truyền thông, kiểm soát rủi ro thương hiệu, rà soát tính chuẩn xác kỹ thuật và cấp lệnh Gate Clearance phát hành."
                }
            },
            {
                "id": "DEPT_SERVICES_WELLNESS",
                "department_name": "Bộ Phận Dịch Vụ & Đời Sống (Căn Tin - Giải Trí - Wellness)",
                "code": "WELLNESS",
                "corporate_sop": "Quy chuẩn Dịch vụ Hậu cần, Căn tin Dinh dưỡng & Chăm sóc Thể chất Nhân viên Doanh nghiệp 2026",
                "barista": {
                    "name": "Nguyễn Thị Trà My",
                    "title": "Barista & Quầy Bar Căn Tin",
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Pha chế cà phê espresso, trà thảo mộc, nước ép dinh dưỡng và phục vụ quầy bar tiếp khách & giờ nghỉ giải lao."
                },
                "chef": {
                    "name": "Trần Văn Bếp",
                    "title": "Bếp Trưởng & Dinh Dưỡng Năng Lượng Doanh Nghiệp",
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Quản lý thực đơn bữa ăn giàu năng lượng, đồ ăn nhẹ giờ nghỉ, kiểm soát tiêu chuẩn ATTP và tái tạo thể chất cho CBNV."
                },
                "specialist": {
                    "name": "Nguyễn Thị Trà My & Trần Văn Bếp",
                    "title": "Nhân viên Dịch vụ Quầy Bar & Bếp Trưởng Dinh Dưỡng",
                    "level": RoleLevel.LEVEL_2_SPECIALIST.name,
                    "mission": "Phục vụ giải khát dinh dưỡng tại quầy bar Căn tin và vận hành khu giải lao, massage, thể dục wellness."
                },
                "head": {
                    "name": "Nguyễn Thị Trà My",
                    "title": "Trưởng Bộ Phận Hậu Cần Dịch Vụ & Đời Sống",
                    "level": RoleLevel.LEVEL_3_HEAD.name,
                    "mission": "Điều phối dịch vụ căn tin quầy bar, duy trì phòng giải trí massage thể dục và tái tạo năng lượng cho toàn bộ công ty."
                }
            }
        ]

    def dispatch_audit(self, workflow_type: str, payload: Dict[str, Any], generate_doc: bool = True) -> Dict[str, Any]:
        """
        Điều phối luồng công việc đến phòng ban chuyên trách qua quy trình 2 cấp:
        1. Chuyên viên chuyên môn thực thi -> Lập hồ sơ kỹ thuật (Dossier)
        2. Trưởng phòng rà soát quy trình, quy định -> Cấp lệnh Gate Clearance
        3. Tự động xuất Báo Cáo Thẩm Tra Riêng Biệt (Standalone Department Report) kèm Word .docx
        4. Nếu ĐẠT và vượt thẩm quyền -> Đưa vào hàng đợi Trình Founder phê duyệt
        """
        wf = workflow_type.upper()
        result = None

        if wf == "CONTRACT":
            result = LegalContractDepartment.audit_contract(
                contract_title=payload.get("contract_title", "Hợp đồng thi công xây dựng"),
                contract_date=payload.get("contract_date", "2026-08-01"),
                contract_value=float(payload.get("contract_value", 0)),
                requested_advance=float(payload.get("requested_advance", 0)),
                has_bank_guarantee=bool(payload.get("has_bank_guarantee", False)),
                clause_texts=payload.get("clause_texts", [])
            )

        elif wf == "BIDDING":
            result = BiddingProcurementDepartment.audit_procurement_package(
                package_name=payload.get("package_name", "Gói thầu xây lắp"),
                package_type=payload.get("package_type", "CONSTRUCTION"),
                estimated_budget=float(payload.get("estimated_budget", 0)),
                is_direct_award=bool(payload.get("is_direct_award", False)),
                vendor_quotes=payload.get("vendor_quotes", []),
                posted_on_procurement_network=bool(payload.get("posted_on_procurement_network", False))
            )

        elif wf == "QS_BOQ":
            result = QSCostEstimatingDepartment.audit_boq_items(
                project_name=payload.get("project_name", "Dự án"),
                boq_items=payload.get("boq_items", []),
                cad_filepath=payload.get("cad_filepath", None)
            )

        elif wf == "QAQC":
            result = QAQCSiteDepartment.audit_inspection_record(
                work_item=payload.get("work_item", "Nghiệm thu bê tông"),
                inspection_date=payload.get("inspection_date", "2026-10-01"),
                test_results_passed=bool(payload.get("test_results_passed", True)),
                logbook_updated=bool(payload.get("logbook_updated", True)),
                asbuilt_stamp_signatures=payload.get("asbuilt_stamp_signatures", [])
            )

        elif wf == "SETTLEMENT":
            result = SettlementAuditDepartment.audit_payment_certificate_08a(
                contract_no=payload.get("contract_no", "HĐ-01"),
                contract_val=float(payload.get("contract_value", 0)),
                previous_paid_val=float(payload.get("previous_paid", 0)),
                current_claim_val=float(payload.get("current_claim", 0)),
                advance_recovered_val=float(payload.get("advance_recovered", 0)),
                warranty_retention_percent=float(payload.get("warranty_percent", 5.0)),
                has_bbntcv=bool(payload.get("has_bbntcv", True))
            )

        elif wf == "MARKETING":
            result = MarketingMediaDepartment.execute_marketing_campaign(
                campaign_title=payload.get("campaign_title", "Chiến dịch Nâng tầm Thương hiệu Xây dựng AI T&T 2026"),
                core_message=payload.get("core_message", "Ứng dụng trí tuệ nhân tạo đột phá trong quản lý dự án xây dựng, minh bạch tài chính và kiểm soát tiến độ tuyệt đối."),
                target_channels=payload.get("target_channels", ["FACEBOOK", "LINKEDIN", "TIKTOK", "YOUTUBE"]),
                highlight_achievements=payload.get("highlight_achievements"),
                video_duration_seconds=int(payload.get("video_duration_seconds", 60)),
                key_video_scenes=payload.get("key_video_scenes"),
                campaign_budget=float(payload.get("campaign_budget", 0))
            )

        else:
            return {"status": "ERROR", "message": f"Loại quy trình không xác định: {workflow_type}"}

        # Lưu thông tin file đính kèm / đường link hồ sơ giao việc cho phòng ban
        result["attached_file_name"] = payload.get("attached_file_name", "")
        result["attached_file_link"] = payload.get("attached_file_link", "")

        # Lưu trữ kết quả mới nhất của phòng ban
        self.latest_dept_results[wf] = result

        # Ghi nhận trạng thái chuyển bước (Gate Transfer Record)
        gate_status = result.get("gate_status", "APPROVED_FOR_TRANSFER")
        gate_record = {
            "workflow": wf,
            "department": result.get("department", ""),
            "gate_status": gate_status,
            "specialist": result.get("personnel", {}).get("specialist", ""),
            "head": result.get("personnel", {}).get("department_head", ""),
            "summary": result.get("summary", "")
        }
        self.gate_transfer_log.append(gate_record)

        # Tự động xuất Báo cáo Riêng Biệt Phòng Ban (Standalone Department Report)
        proj_name = payload.get("project_name", payload.get("contract_title", payload.get("package_name", "Dự án T&T Tower")))
        standalone_rep = reporting_engine.generate_standalone_department_report(
            workflow_type=wf,
            result_data=result,
            project_name=proj_name,
            export_docx=generate_doc
        )
        result["standalone_report"] = standalone_rep
        self.generated_reports.append(standalone_rep)

        # Kiểm tra nếu cần Founder phê duyệt (Human-in-the-Loop)
        if result.get("requires_founder_approval"):
            approval_item = {
                "id": f"APP-{len(self.pending_approvals) + 1:04d}",
                "workflow": wf,
                "summary": result.get("summary", ""),
                "department": result.get("department", ""),
                "gate_status": gate_status,
                "status": "CHỜ FOUNDER DUYỆT",
                "personnel": result.get("personnel", {}),
                "data": result,
                "report_code": standalone_rep["report_code"],
                "docx_path": standalone_rep.get("docx_path")
            }
            self.pending_approvals.append(approval_item)
            result["approval_id"] = approval_item["id"]

        self.history_records.append(result)
        return result

    def generate_modular_report(
        self,
        selected_workflows: List[str],
        custom_payloads: Optional[Dict[str, Any]] = None,
        report_theme: str = "Báo Cáo Tổng Hợp Chuyên Đề Theo Yêu Cầu",
        project_name: str = "Dự án Tổ hợp T&T Tower"
    ) -> Dict[str, Any]:
        """
        Sinh Báo Cáo Tổng Hợp Chuyên Đề khi người dùng chỉ yêu cầu một nhóm quy trình (1-4 phòng ban).
        """
        wf_results = {}
        for wf in selected_workflows:
            wf_key = wf.upper()
            if custom_payloads and wf_key in custom_payloads:
                wf_results[wf_key] = self.dispatch_audit(wf_key, custom_payloads[wf_key], generate_doc=False)
            elif wf_key in self.latest_dept_results:
                wf_results[wf_key] = self.latest_dept_results[wf_key]
            else:
                # Chạy mẫu mặc định cho phòng ban đó
                dummy_payload = self._get_default_payload_for_wf(wf_key)
                wf_results[wf_key] = self.dispatch_audit(wf_key, dummy_payload, generate_doc=False)

        modular_rep = reporting_engine.generate_modular_report(
            selected_workflows=selected_workflows,
            workflow_results=wf_results,
            report_theme=report_theme,
            project_name=project_name,
            export_docx=True
        )
        self.generated_reports.append(modular_rep)
        return modular_rep

    def generate_master_company_report(
        self,
        project_name: str = "Tổ hợp Thương mại & Văn phòng T&T Tower",
        project_code: str = "DA-TT-2026-HQ",
        custom_payloads: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sinh Bản Báo Cáo Tổng Thể Toàn Diện của Công Ty (Master Executive Dossier)
        kèm đầy đủ báo cáo chuyên môn của toàn bộ 6 phòng ban:
        1. Pháp chế & Hợp đồng (NĐ 210/2026)
        2. Đấu thầu & Mua sắm (NĐ 349/2026)
        3. Dự toán QS & BOQ (TT 09/2024)
        4. Quản lý Chất lượng QA/QC (NĐ 06/2021)
        5. Kiểm toán Thanh Quyết toán (NĐ 99/2021)
        6. Marketing & Truyền thông Thương hiệu (Chiến lược Đa kênh & Video Quảng cáo)
        """
        all_wfs = ["CONTRACT", "BIDDING", "QS_BOQ", "QAQC", "SETTLEMENT", "MARKETING"]
        all_results = {}

        for wf in all_wfs:
            if custom_payloads and wf in custom_payloads:
                all_results[wf] = self.dispatch_audit(wf, custom_payloads[wf], generate_doc=False)
            elif wf in self.latest_dept_results:
                all_results[wf] = self.latest_dept_results[wf]
            else:
                dummy_payload = self._get_default_payload_for_wf(wf)
                all_results[wf] = self.dispatch_audit(wf, dummy_payload, generate_doc=False)

        master_rep = reporting_engine.generate_master_company_report(
            all_departments_results=all_results,
            project_name=project_name,
            project_code=project_code,
            export_docx=True
        )
        self.generated_reports.append(master_rep)
        return master_rep

    def _get_default_payload_for_wf(self, wf: str) -> Dict[str, Any]:
        """Dữ liệu dự toán / nghiệm thu chuẩn mực mặc định phục vụ kiểm thử"""
        if wf == "CONTRACT":
            return {
                "contract_title": "Hợp đồng thi công cọc khoan nhồi T&T Tower",
                "contract_date": "2026-08-01",
                "contract_value": 15000000000,
                "requested_advance": 4000000000,
                "has_bank_guarantee": True,
                "clause_texts": ["Thời hạn thanh toán trong vòng 14 ngày làm việc kể từ ngày nhận đủ hồ sơ Mẫu 08a."]
            }
        elif wf == "BIDDING":
            return {
                "package_name": "Gói thầu cơ điện trạm biến áp",
                "package_type": "CONSTRUCTION",
                "estimated_budget": 4800000000,
                "is_direct_award": True,
                "posted_on_procurement_network": True,
                "vendor_quotes": [
                    {"vendor": "Công ty ALPHA", "price": 4700000000},
                    {"vendor": "Công ty BETA", "price": 4800000000},
                    {"vendor": "Công ty GAMMA", "price": 7200000000}
                ]
            }
        elif wf == "QS_BOQ":
            return {
                "project_name": "Tổ hợp Thương mại T&T",
                "boq_items": [
                    {"name": "Đào đất móng công trình", "unit": "m3", "qty": 2000, "unit_price": 65000, "norm_code": "AB.11111"},
                    {"name": "Bê tông lót móng đá 4x6 mác 100", "unit": "m3", "qty": 300, "unit_price": 1150000, "norm_code": "AF.11111"}
                ]
            }
        elif wf == "QAQC":
            return {
                "work_item": "Nghiệm thu đổ bê tông sàn Tầng 3",
                "inspection_date": "2026-11-05",
                "test_results_passed": True,
                "logbook_updated": True,
                "asbuilt_stamp_signatures": [
                    "Người lập bản vẽ hoàn công",
                    "Người đại diện theo pháp luật của Nhà thầu thi công xây dựng",
                    "Người đại diện theo pháp luật của Nhà thầu tư vấn giám sát",
                    "Chủ nhiệm giám sát thi công xây dựng"
                ]
            }
        elif wf == "SETTLEMENT":
            return {
                "contract_no": "HĐ-TT-2026-08",
                "contract_value": 15000000000,
                "previous_paid": 5000000000,
                "current_claim": 2000000000,
                "advance_recovered": 400000000,
                "warranty_percent": 5.0,
                "has_bbntcv": True
            }
        elif wf == "MARKETING":
            return {
                "campaign_title": "Chiến dịch Truyền thông Nâng tầm Thương hiệu Xây dựng AI T&T Tower 2026",
                "core_message": "T&T AI Construction Enterprise: Tiên phong ứng dụng AI điều hành thi công, chuẩn mực Pháp lý Xây dựng 2026 và kiểm soát dòng tiền CĐT minh bạch 100%.",
                "target_channels": ["FACEBOOK", "LINKEDIN", "TIKTOK", "YOUTUBE"],
                "video_duration_seconds": 60,
                "campaign_budget": 35000000
            }
        return {}

    def assign_task(
        self,
        task_title: str,
        project_name: str,
        assigned_workflows: List[str],
        priority: str = "URGENT",
        deadline: str = "2026-11-15",
        founder_instruction: str = "",
        custom_payloads: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Founder Mai Quang Vinh giao việc trực tiếp cho 1 phòng ban, một nhóm phòng ban hoặc toàn bộ công ty.
        Hệ thống tự động điều phối:
        1. Chuyên viên chuyên môn thực thi bóc tách kỹ thuật
        2. Trưởng phòng kiểm duyệt quy trình, quy chuẩn 2026 & cấp lệnh Gate Clearance
        3. Xuất báo cáo tương ứng (Báo cáo riêng phòng ban / Báo cáo chuyên đề / Báo cáo tổng thể công ty)
        """
        import datetime
        task_id = f"TASK-{len(self.assigned_tasks) + 1:04d}"
        created_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        wfs = [w.upper() for w in assigned_workflows if w]
        if not wfs:
            wfs = ["CONTRACT"]

        step_logs = []
        dept_results = {}

        for wf in wfs:
            custom_wf_payload = (custom_payloads or {}).get(wf) or {}
            base_payload = self._get_default_payload_for_wf(wf)
            base_payload.update(custom_wf_payload)
            base_payload["project_name"] = project_name
            res = self.dispatch_audit(wf, base_payload, generate_doc=True)
            dept_results[wf] = res
            standalone_rep = res.get("standalone_report", {})
            step_logs.append({
                "workflow": wf,
                "department": res.get("department", wf),
                "specialist": res.get("personnel", {}).get("specialist", ""),
                "department_head": res.get("personnel", {}).get("department_head", ""),
                "gate_status": res.get("gate_status", "APPROVED_FOR_TRANSFER"),
                "summary": res.get("summary", ""),
                "attached_file_name": res.get("attached_file_name", ""),
                "attached_file_link": res.get("attached_file_link", ""),
                "standalone_report_code": standalone_rep.get("report_code", ""),
                "docx_path": standalone_rep.get("docx_path", ""),
                "markdown": standalone_rep.get("markdown", "")
            })

        # Xuất báo cáo tổng hợp tương ứng với phạm vi giao việc
        if len(wfs) == 1:
            only_wf = wfs[0]
            primary_report = dept_results[only_wf].get("standalone_report", {})
            execution_mode = "GIAO VIỆC ĐỘC LẬP 01 PHÒNG BAN"
        elif len(wfs) >= 6:
            primary_report = self.generate_master_company_report(
                project_name=project_name,
                project_code=f"DA-{task_id}"
            )
            execution_mode = "GIAO VIỆC TỔNG THỂ TOÀN CÔNG TY (6 PHÒNG BAN)"
        else:
            primary_report = self.generate_modular_report(
                selected_workflows=wfs,
                report_theme=f"Báo Cáo Thực Hiện Nhiệm Vụ: {task_title}",
                project_name=project_name
            )
            execution_mode = f"GIAO VIỆC LIÊN PHÒNG BAN ({len(wfs)} PHÒNG BAN)"

        task_record = {
            "task_id": task_id,
            "task_title": task_title,
            "project_name": project_name,
            "priority": priority,
            "deadline": deadline,
            "founder_instruction": founder_instruction,
            "execution_mode": execution_mode,
            "assigned_workflows": wfs,
            "created_at": created_at,
            "status": "ĐÃ HOÀN THÀNH THẨM TRA & XUẤT BÁO CÁO",
            "step_logs": step_logs,
            "primary_report": primary_report
        }
        self.assigned_tasks.append(task_record)
        return task_record

    def founder_action(self, approval_id: str, action: str, note: str = "") -> Dict[str, Any]:
        """
        Founder Mai Quang Vinh đưa ra quyết định tối cao: 'APPROVE' / 'REJECT' / 'REVISE'
        """
        for item in self.pending_approvals:
            if item["id"] == approval_id:
                if action == "APPROVE":
                    item["status"] = "ĐÃ ĐƯỢC FOUNDER PHÊ DUYỆT"
                    item["note"] = note
                    return {"success": True, "message": f"Founder {self.founder_name} đã PHÊ DUYỆT hồ sơ {approval_id}!"}
                elif action == "REJECT":
                    item["status"] = "FOUNDER BÁC BỎ"
                    item["note"] = note
                    return {"success": True, "message": f"Founder {self.founder_name} đã TỪ CHỐI hồ sơ {approval_id}!"}
                elif action == "REVISE":
                    item["status"] = "YÊU CẦU SỬA ĐỔI"
                    item["note"] = note
                    return {"success": True, "message": f"Hồ sơ {approval_id} chuyển về phòng ban chỉnh sửa theo chỉ đạo của Founder!"}

        return {"success": False, "message": "Không tìm thấy mã hồ sơ."}

# Global Orchestrator
orchestrator = ConstructionCompanyOrchestrator()
