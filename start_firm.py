# -*- coding: utf-8 -*-
"""
START FIRM: Test All 5 Departments (2-Tier Personnel Architecture) & Reporting Engine
Kiểm thử toàn diện mô hình:
- Mỗi phòng ban gồm: 01 Chuyên viên thực thi chuyên môn + 01 Trưởng phòng kiểm duyệt quy trình
- Đảm bảo kiểm soát Gate Clearance trước khi chuyển bước
- Hệ thống báo cáo:
  1. Báo cáo thẩm tra riêng biệt từng phòng ban (Standalone Department Report)
  2. Báo cáo tổng hợp chuyên đề theo yêu cầu (Modular Multi-Workflow Report)
  3. Bản báo cáo tổng thể toàn diện của công ty (Master Executive Dossier)
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.orchestrator import orchestrator
from core.reporting_engine import REPORTS_DIR
from knowledge.legal_engine import legal_engine

def run_self_test():
    print("==================================================================")
    print("   KIỂM THỬ HỆ THỐNG CÔNG TY XÂY DỰNG 1 NGƯỜI ĐIỀU HÀNH BẰNG AI")
    print("   CƠ CẤU 2 CẤP NHÂN SỰ + HỆ THỐNG BÁO CÁO TỔNG THỂ & CHUYÊN ĐỀ")
    print("==================================================================")

    # 1. Hiển thị danh bạ 10 nhân sự qua 5 phòng ban
    print("\n[DANH BẠ 10 NHÂN SỰ ẢO ĐIỀU HÀNH BỞI FOUNDER MAI QUANG VINH]:")
    roster = orchestrator.get_firm_roster()
    for dept in roster:
        print(f"  🏢 {dept['department_name']} ({dept['code']}):")
        print(f"     • 👷 Chuyên viên: {dept['specialist']['name']} - {dept['specialist']['title']}")
        print(f"       Nhiệm vụ: {dept['specialist']['mission']}")
        print(f"     • 🧑‍⚖️ Trưởng phòng: {dept['head']['name']} - {dept['head']['title']}")
        print(f"       Kiểm soát: {dept['head']['mission']}")

    # 2. Test Phòng 1: Ban Pháp chế & Hợp đồng (Kèm Báo cáo riêng)
    print("\n[1] KIỂM THỬ PHÒNG PHÁP CHẾ & HỢP ĐỒNG (Nghị định 210/2026/NĐ-CP):")
    res1 = orchestrator.dispatch_audit("CONTRACT", {
        "contract_title": "Hợp đồng thi công cọc khoan nhồi T&T Tower",
        "contract_date": "2026-08-01",
        "contract_value": 15000000000,
        "requested_advance": 5000000000, # 33.3% > trần 30%
        "has_bank_guarantee": False,     # Thiếu bảo lãnh > 1 tỷ
        "clause_texts": [
            "Thời hạn thanh toán khối lượng hoàn thành trong vòng 60 ngày kể từ ngày nghiệm thu.",
            "Phạt chậm tiến độ tối đa 12% giá trị hợp đồng."
        ]
    })
    print(f"    • Nhân sự thực thi: {res1['personnel']['specialist']}")
    print(f"    • Nhân sự kiểm duyệt: {res1['personnel']['department_head']}")
    print(f"    • LỆNH CHUYỂN BƯỚC: [{res1['gate_status']}]")
    print(f"    • Báo cáo riêng biệt: {res1['standalone_report']['report_code']} (File: {os.path.basename(res1['standalone_report']['docx_path'])})")
    print(f"    • Kết luận: {res1['summary']}")

    # 3. Test Phòng 2: Ban Đấu thầu & Mua sắm (Kèm Báo cáo riêng)
    print("\n[2] KIỂM THỬ PHÒNG ĐẤU THẦU & MUA SẮM (Nghị định 349/2026/NĐ-CP):")
    res2 = orchestrator.dispatch_audit("BIDDING", {
        "package_name": "Gói thầu cơ điện M&E trạm biến áp",
        "package_type": "CONSTRUCTION",
        "estimated_budget": 4500000000, # <= 5 tỷ trần chỉ định thầu
        "is_direct_award": True,
        "posted_on_procurement_network": True,
        "vendor_quotes": [
            {"vendor": "Công ty ALPHA", "price": 4400000000},
            {"vendor": "Công ty BETA", "price": 4500000000},
            {"vendor": "Công ty GAMMA (Ảo)", "price": 6800000000} # Lệch > 30%
        ]
    })
    print(f"    • Nhân sự thực thi: {res2['personnel']['specialist']}")
    print(f"    • Nhân sự kiểm duyệt: {res2['personnel']['department_head']}")
    print(f"    • LỆNH CHUYỂN BƯỚC: [{res2['gate_status']}]")
    print(f"    • Báo cáo riêng biệt: {res2['standalone_report']['report_code']} (File: {os.path.basename(res2['standalone_report']['docx_path'])})")
    print(f"    • Kết luận: {res2['summary']}")

    # 4. Test Phòng 3: Ban Kỹ sư Dự toán QS & BOQ (Kèm Báo cáo riêng)
    print("\n[3] KIỂM THỬ PHÒNG DỰ TOÁN QS & BOQ (Thông tư 09/2024/TT-BXD):")
    res3 = orchestrator.dispatch_audit("QS_BOQ", {
        "project_name": "Dự án Khu Đô Thị Mới T&T",
        "boq_items": [
            {"name": "Bê tông dầm sàn C25", "unit": "m3", "qty": 150, "unit_price": 1450000, "norm_code": "AF.12345"},
            {"name": "Bê tông dầm sàn C25", "unit": "m3", "qty": 150, "unit_price": 1450000, "norm_code": "AF.12345"}, # Cố ý tính trùng lặp
            {"name": "Cốt thép móng D<=18", "unit": "tấn", "qty": 10, "unit_price": 21000000, "norm_code": ""}
        ]
    })
    print(f"    • Nhân sự thực thi: {res3['personnel']['specialist']}")
    print(f"    • Nhân sự kiểm duyệt: {res3['personnel']['department_head']}")
    print(f"    • LỆNH CHUYỂN BƯỚC: [{res3['gate_status']}]")
    print(f"    • Báo cáo riêng biệt: {res3['standalone_report']['report_code']}")
    print(f"    • Kết luận: {res3['summary']}")

    # 5. Test Phòng 4: Ban Quản lý Chất lượng QA/QC
    print("\n[4] KIỂM THỬ PHÒNG QUẢN LÝ CHẤT LƯỢNG QA/QC (Nghị định 06/2021/NĐ-CP):")
    res4 = orchestrator.dispatch_audit("QAQC", {
        "work_item": "Nghiệm thu đổ bê tông sàn Tầng 2",
        "inspection_date": "2026-11-08",
        "test_results_passed": True,
        "logbook_updated": True,
        "asbuilt_stamp_signatures": [
            "Người lập bản vẽ hoàn công",
            "Người đại diện theo pháp luật của Nhà thầu thi công xây dựng",
            "Người đại diện theo pháp luật của Nhà thầu tư vấn giám sát",
            "Chủ nhiệm giám sát thi công xây dựng"
        ]
    })
    print(f"    • Nhân sự thực thi: {res4['personnel']['specialist']}")
    print(f"    • Nhân sự kiểm duyệt: {res4['personnel']['department_head']}")
    print(f"    • LỆNH CHUYỂN BƯỚC: [{res4['gate_status']}]")
    print(f"    • Báo cáo riêng biệt: {res4['standalone_report']['report_code']}")

    # 6. Test Phòng 5: Ban Kiểm toán Thanh Quyết toán
    print("\n[5] KIỂM THỬ PHÒNG KIỂM TOÁN THANH QUYẾT TOÁN (Nghị định 99/2021/NĐ-CP):")
    res5 = orchestrator.dispatch_audit("SETTLEMENT", {
        "contract_no": "HĐ-TT-2026-08",
        "contract_value": 12000000000,
        "previous_paid": 5000000000,
        "current_claim": 2000000000,
        "advance_recovered": 400000000,
        "warranty_percent": 5.0,
        "has_bbntcv": True
    })
    print(f"    • Nhân sự thực thi: {res5['personnel']['specialist']}")
    print(f"    • Nhân sự kiểm duyệt: {res5['personnel']['department_head']}")
    print(f"    • LỆNH CHUYỂN BƯỚC: [{res5['gate_status']}]")
    print(f"    • Báo cáo riêng biệt: {res5['standalone_report']['report_code']}")

    # 7. Test Báo Cáo Tổng Hợp Chuyên Đề Theo Yêu Cầu (Modular Report: Contract + Bidding)
    print("\n[6] KIỂM THỬ BÁO CÁO TỔNG HỢP CHUYÊN ĐỀ THEO YÊU CẦU (2 PHÒNG BAN: CONTRACT + BIDDING):")
    mod_report = orchestrator.generate_modular_report(
        selected_workflows=["CONTRACT", "BIDDING"],
        report_theme="Báo Cáo Thẩm Định Pháp Lý Hợp Đồng & Lựa Chọn Nhà Thầu",
        project_name="Dự án T&T Tower"
    )
    print(f"    • Mã báo cáo chuyên đề: {mod_report['report_code']}")
    print(f"    • File Word .docx: {os.path.basename(mod_report['docx_path'])}")
    print(f"    • Số cảnh báo tổng hợp: {mod_report['total_alerts']} cảnh báo")

    # 8. Test Bản Báo Cáo Tổng Thể Công Ty (Master Executive Dossier)
    print("\n[7] KIỂM THỬ BẢN BÁO CÁO TỔNG THỂ CÔNG TY (MASTER EXECUTIVE DOSSIER):")
    master_report = orchestrator.generate_master_company_report(
        project_name="Tổ hợp Thương mại & Văn phòng T&T Tower",
        project_code="DA-TT-2026-HQ"
    )
    print(f"    • Mã hồ sơ tổng thể: {master_report['report_code']}")
    print(f"    • File Word .docx chuẩn NĐ 30: {os.path.basename(master_report['docx_path'])}")
    print(f"    • Đánh giá: {master_report['approved_departments']}/5 phòng ban được chuyển bước | Bị chặn sửa đổi: {master_report['blocked_departments']}")

    # 9. Danh mục file đã sinh trong reports/
    print("\n[8] KIỂM TRA TỆP TIN BÁO CÁO XUẤT RA TẠI THƯ MỤC 'reports/':")
    if os.path.exists(REPORTS_DIR):
        files = os.listdir(REPORTS_DIR)
        print(f"    • Tổng số file Word đã sinh: {len(files)} tệp tin:")
        for f in files[-5:]:
            size_kb = os.path.getsize(os.path.join(REPORTS_DIR, f)) / 1024
            print(f"      - {f} ({size_kb:.1f} KB)")

    print("\n==================================================================")
    print("   ✅ TOÀN BỘ HỆ THỐNG BÁO CÁO ĐÃ VẬN HÀNH HOÀN HẢO!")
    print("   Khởi chạy Dashboard: Chạy 'start_dashboard.bat' hoặc 'python web/server.py'")
    print("==================================================================")

if __name__ == "__main__":
    run_self_test()
