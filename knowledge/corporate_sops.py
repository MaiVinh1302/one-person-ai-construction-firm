# -*- coding: utf-8 -*-
"""
CORPORATE SOPs & TEMPLATES ENGINE (HỆ THỐNG QUY TRÌNH & BIỂU MẪU NỘI BỘ TẬP ĐOÀN)
Chắt lọc từ kho dữ liệu thực tế:
D:\\OneDrive - CONG TY CO PHAN TAP DOAN T&T\\VINH\\CÁC QUY TRÌNH THỰC HIỆN

Kết hợp chặt chẽ giữa:
1. Pháp luật Xây dựng Nhà nước 2026 (NĐ 210/2026/NĐ-CP, NĐ 349/2026/NĐ-CP, NĐ 06/2021, NĐ 99/2021, TT 09/2024)
2. Quy chế, Quy định & Bộ Biểu mẫu Nội bộ Tập đoàn T&T (QĐ 690, QĐ 560, QĐ 419/420/421, QĐ 516/517, QĐ 458, QĐ 122/123, QT01-XLPS)
"""

import os
from typing import Dict, List, Any, Optional

SOP_ROOT_DIR = r"D:\OneDrive - CONG TY CO PHAN TAP DOAN T&T\VINH\CÁC QUY TRÌNH THỰC HIỆN"


# ==============================================================================
# 1. TRỤ CỘT 1: BỘ HỢP ĐỒNG MẪU XÂY DỰNG & CUNG ỨNG (QĐ 690/QĐ-TGĐ & QĐ 560/QĐ-TGĐ)
# Áp dụng cho: Phòng Pháp chế & Đàm phán Hợp đồng (DEPT_LEGAL)
# ==============================================================================
STANDARD_CONTRACT_TEMPLATES = {
    "NDA_ANTI_CORRUPTION": {
        "code": "XDCK.2024.01 & 02",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Bản cam kết bảo mật thông tin và chống tham nhũng, gian lận (Song ngữ Việt - Anh)",
        "condition": "Bắt buộc ký kèm tất cả các gói thầu/hợp đồng xây dựng và cung ứng",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24\1. Ban Cam ket bao mat thong tin va Chong tham nhung, gian lan (VN) - XDCK.2024.01.docx"
    },
    "CONSTRUCTION_OVER_3B": {
        "code": "XDTC.2024.01",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Hợp đồng thi công xây dựng công trình (Giá trị >= 3 tỷ đồng)",
        "condition": "Áp dụng cho gói thầu thi công xây lắp có giá trị từ 03 tỷ đồng trở lên",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24\3. HD thi cong xay dung (tren 3 ty) - XDTC.2024.01.docx"
    },
    "CONSTRUCTION_UNDER_3B": {
        "code": "XDTC.2024.02",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Hợp đồng thi công xây dựng công trình (Giá trị < 3 tỷ đồng)",
        "condition": "Áp dụng cho gói thầu thi công xây lắp có giá trị dưới 03 tỷ đồng",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24\4. HD thi cong xay dung (duoi 3 ty) - XDTC.2024.02.docx"
    },
    "CONSTRUCTION_MEP": {
        "code": "XDTC.2024.03",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Hợp đồng cung cấp vật tư, thiết bị và thi công hệ thống Cơ điện (MEP)",
        "condition": "Áp dụng cho gói thầu Cơ điện, PCCC, Trạm biến áp, ĐHKK, Điện nhẹ",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24\5. HD cung cap vat tu, thiet bi va thi cong MEP - XDTC.2024.03.docx"
    },
    "CONSTRUCTION_ALUMINUM_GLASS": {
        "code": "XDTC.2024.04",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Hợp đồng cung cấp và lắp đặt Nhôm kính - Mặt dựng",
        "condition": "Áp dụng cho gói thầu Nhôm kính ngoài nhà và vách kính",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24"
    },
    "CONSTRUCTION_INTERIOR": {
        "code": "XDTC.2024.05",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Hợp đồng cung cấp và thi công Nội thất",
        "condition": "Áp dụng cho gói thầu hoàn thiện nội thất liền tường và đồ rời",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24"
    },
    "GENERAL_CONTRACTOR": {
        "code": "XDTC.2024.07 & 08",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Hợp đồng Tổng thầu thi công xây dựng & Phụ lục Tổng thầu",
        "condition": "Áp dụng cho gói thầu Tổng thầu Design & Build hoặc Tổng thầu thi công",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24"
    },
    "CONSULTANCY_CONTRACTS": {
        "code": "XDTV.2024.01 -> 19",
        "decision": "QĐ 690/QĐ-TGĐ (31/12/2024)",
        "name": "Bộ 19 mẫu Hợp đồng Tư vấn (Quy hoạch, TK Kiến trúc, Nội thất, PCCC, Thẩm tra, Khảo sát, TVGS, QLDA, ĐTM)",
        "condition": "Áp dụng cho toàn bộ các gói thầu dịch vụ tư vấn dự án",
        "rel_path": r"2024 Hop dong mau (XD, CU)\1. QD 690-Ban hanh mau HD Xay dung (30 mau)-31.12.24"
    },
    "SUPPLY_CONTRACTS": {
        "code": "HDCMB.2024.01 -> 06 & HDM_01 -> 06",
        "decision": "QĐ 560/QĐ-TGĐ (Đợt 1 & Đợt 2)",
        "name": "Bộ 14 mẫu Hợp đồng Cung ứng vật tư, thiết bị 3 bên, liên danh, thuê máy móc & Cây xanh (XDDV.2024.19)",
        "condition": "Áp dụng cho gói thầu mua sắm hàng hóa, vật tư CĐT cấp hoặc hợp đồng 3 bên",
        "rel_path": r"2024 Hop dong mau (XD, CU)\2. QD 560-Ban hanh mau HD Cung ung (8 mau dot 1)"
    }
}

LEGAL_CORPORATE_RULES = [
    "Bắt buộc sử dụng đúng mẫu hợp đồng theo phân loại giá trị tại QĐ 690/QĐ-TGĐ (XDTC.2024.01 cho HĐ >= 3 tỷ; XDTC.2024.02 cho HĐ < 3 tỷ; XDTC.2024.03 cho MEP).",
    "Bắt buộc đính kèm Bản cam kết bảo mật thông tin và chống tham nhũng, gian lận (Mẫu XDCK.2024.01).",
    "Trần tạm ứng tối đa 30% giá trị hợp đồng; tạm ứng > 1 tỷ đồng bắt buộc có Bảo lãnh tạm ứng ngân hàng (NĐ 210/2026/NĐ-CP).",
    "Thời hạn hiệu lực của Bảo lãnh thực hiện hợp đồng và Bảo lãnh tiền tạm ứng phải >= Thời gian thực hiện hợp đồng + tối thiểu 30 ngày (Quy định TQT QĐ 122/123).",
    "Mọi điều khoản sửa đổi khác với Hợp đồng mẫu QĐ 690/QĐ 560 bắt buộc phải lập Bảng so sánh điều khoản khác biệt trình Pháp chế & Founder phê duyệt."
]


# ==============================================================================
# 2. TRỤ CỘT 2: QUY HOẠCH GÓI THẦU, QUY ĐỊNH LCNT & 33 MẪU HSMT CHUẨN (QĐ 419/420/421, QĐ 516/517, QĐ 458)
# Áp dụng cho: Phòng Quản lý Đấu thầu & Mua sắm (DEPT_BIDDING)
# ==============================================================================
BIDDING_PACKAGE_GROUPS = [
    {"group_code": "NHÓM I", "name": "Các gói thầu giai đoạn Tiền dự án", "count": 17, "examples": "Khảo sát địa hình, rà phá bom mìn, lập QH 1/500, ĐTM, thỏa thuận đấu nối"},
    {"group_code": "NHÓM II", "name": "Các gói thầu Tư vấn Thiết kế & QLTC", "count": 15, "examples": "Tư vấn TK cơ sở, TKKT, BVTC, Thẩm tra, TVGS, Kiểm định chất lượng"},
    {"group_code": "NHÓM III", "name": "Các gói thầu Thi công Xây lắp", "count": 20, "examples": "San lấp, Cọc đại trà & thí nghiệm, Kết cấu thân, Hoàn thiện, HTKT, MEP, PCCC, Nhôm kính"},
    {"group_code": "NHÓM IV", "name": "Các gói thầu Cung ứng Thiết bị & Vật tư", "count": 13, "examples": "Thang máy, Máy phát điện, Trạm biến áp, Tủ hạ thế, ĐHKK, Đá ốp lát, Thiết bị vệ sinh, Cây xanh"}
]

BIDDING_LCNT_TEMPLATES = [
    {"code": "BM0-PYC", "name": "Phiếu yêu cầu lựa chọn nhà thầu / nhà cung cấp", "stage": "Chuẩn bị đấu thầu"},
    {"code": "BM00-TTC", "name": "Bảng thông tin chung về gói thầu & kế hoạch LCNT", "stage": "Chuẩn bị đấu thầu"},
    {"code": "BM01-DSN", "name": "Tờ trình phê duyệt Danh sách ngắn nhà thầu mời thầu", "stage": "Sơ tuyển / Mời thầu"},
    {"code": "BM02-TMT", "name": "Thư mời thầu & Biên bản phát hành HSMT", "stage": "Phát hành HSMT"},
    {"code": "BM02A", "name": "Biên bản làm rõ Hồ sơ mời thầu (HSMT)", "stage": "Làm rõ HSMT"},
    {"code": "BM03-BBMT", "name": "Biên bản mở Hồ sơ dự thầu (HSĐXKT / HSĐXTC)", "stage": "Mở thầu"},
    {"code": "BM04-BCDGKT", "name": "Báo cáo đánh giá Hồ sơ đề xuất Kỹ thuật (Làm rõ tối đa 01 lần)", "stage": "Đánh giá Kỹ thuật"},
    {"code": "BM05-BC Giá", "name": "Báo cáo đánh giá Hồ sơ đề xuất Tài chính / Giá dự thầu", "stage": "Đánh giá Tài chính"},
    {"code": "BM06", "name": "Báo cáo đánh giá sau đàm phán thương thảo", "stage": "Sau đàm phán"},
    {"code": "BM07-BBĐP", "name": "Biên bản đàm phán Hợp đồng với Nhà thầu xếp hạng 1", "stage": "Đàm phán HĐ"},
    {"code": "BM08-TTr PDKQLCNT", "name": "Tờ trình phê duyệt Kết quả lựa chọn nhà thầu", "stage": "Trình duyệt KQLCNT"},
    {"code": "BM09A / BM09B", "name": "Thông báo trúng thầu (09A) & Thông báo không trúng thầu (09B)", "stage": "Trao thầu"}
]

HSMT_STANDARD_TEMPLATES_QD458 = {
    "BM12": "HSMT Gói thầu Thi công Xây lắp chính (Kết cấu & Hoàn thiện)",
    "BM13": "HSMT Gói thầu Thi công Hệ thống Cơ điện (MEP)",
    "BM13A": "HSMT Gói thầu Thi công Hệ thống Điện nhẹ (ELV)",
    "BM14": "HSMT Gói thầu Trạm xử lý nước thải (XLNT)",
    "BM15": "HSMT Gói thầu Trạm xử lý nước sạch (XLNS)",
    "BM16": "HSMT Gói thầu Thi công Nền móng & Cọc khoan nhồi / Cọc ép",
    "BM17": "HSMT Gói thầu Cung cấp & lắp đặt Cửa gỗ, cửa chống cháy",
    "BM18": "HSMT Gói thầu Cung cấp & thi công Đá ốp lát",
    "BM20/28": "HSMT Gói thầu Cung cấp & lắp đặt Nhôm kính - Mặt dựng",
    "BM21": "HSMT Gói thầu Thi công Hệ thống PCCC",
    "BM22": "HSMT Gói thầu Chiếu sáng mặt đứng (Facade Lighting)",
    "BM25": "HSMT Gói thầu Thi công Nội thất",
    "BM32": "HSMT Gói thầu Cung cấp & lắp đặt Trạm biến áp",
    "BM33": "HSMT Gói thầu Cung cấp & lắp đặt Máy phát điện",
    "BM34": "HSMT Gói thầu Cung cấp Tủ điện hạ thế (MSB/DB)",
    "BM35": "HSMT Gói thầu Cung cấp & lắp đặt Thang máy",
    "BM40": "HSMT Gói thầu Hệ thống Điều hòa không khí & Thông gió (HVAC)",
    "BM41": "HSMT Gói thầu Thi công Cảnh quan & Cây xanh"
}


# ==============================================================================
# 3. TRỤ CỘT 3: CHUẨN HÓA HSMT 8 BILL & QUY TRÌNH XỬ LÝ PHÁT SINH 12 BƯỚC (QT01-XLPS)
# Áp dụng cho: Phòng Kỹ sư Dự toán QS & BOQ (DEPT_QS)
# ==============================================================================
HSMT_8_BILLS_STANDARD = [
    {
        "bill_no": "Bill 1. CPC",
        "title": "Chi phí hạng mục chung & Phân chia trách nhiệm CĐT - Nhà thầu",
        "key_rule": "Bao gồm Bảo lãnh, bảo hiểm, lán trại, ATLĐ, PCCC, vệ sinh môi trường, quan trắc, hoàn trả hạ tầng. CĐT chỉ thu tiền điện nước từ Nhà thầu chính; chi phí điện nước chạy thử liên động không tải/có tải do CĐT chi trả."
    },
    {
        "bill_no": "Bill 2. Tổng hợp",
        "title": "Bảng tổng hợp giá trị gói thầu",
        "key_rule": "Chi phí chung và các công tác chuẩn bị (Bill 1) được khống chế TRẦN TỐI ĐA = 5% chi phí trực tiếp của gói thầu."
    },
    {
        "bill_no": "Bill 3. BOQ",
        "title": "Bảng tiên lượng mời thầu chuẩn hóa",
        "key_rule": "Tách rõ Phần I (Khối lượng công việc theo hồ sơ thiết kế HSMT) và Phần II (Các hạng mục nhà thầu chào bổ sung ngoài thiết kế nếu phát hiện thiếu sót)."
    },
    {
        "bill_no": "Bill 4. Nguyên tắc đo bóc KL",
        "title": "Nguyên tắc đo bóc khối lượng & Nghiệm thu thanh quyết toán",
        "key_rule": "Chiều cao tính từ cốt ±0.00 (thi công >6m tính vận chuyển lên cao); đo bóc theo kích thước hình học thiết kế không tính lớp vữa trát/ốp lát. NGUYÊN TẮC VÀNG: Khối lượng TQT xác nhận = MIN(Khối lượng Bản vẽ hoàn công, Khối lượng Biên bản nghiệm thu, Khối lượng Hợp đồng/BPTC được duyệt)."
    },
    {
        "bill_no": "Bill 5. PL điều chỉnh",
        "title": "Phụ lục đơn giá điều chỉnh khi thay đổi cấp phối / chủng loại",
        "key_rule": "Quy định sẵn chênh lệch đơn giá khi thay đổi Mác BTTP, thay đổi độ sụt (01 cấp độ sụt = 2cm), bổ sung phụ gia ninh kết nhanh R7/R14 hoặc phụ gia chống thấm B6/B8/B10/B12."
    },
    {
        "bill_no": "Bill 6. Độ sụt BTTP",
        "title": "Bảng quy định độ sụt bê tông thương phẩm bắt buộc",
        "key_rule": "Cao tầng: BT lót/nền 12±2cm; Đài/giằng móng 14±2cm; Cột/vách (<20 tầng: 16±2cm, 20-40 tầng: 18±2cm, >=40 tầng: 20±2cm); Dầm sàn (<20 tầng: 16±2cm, >=20 tầng: 18±2cm). Thấp tầng biệt thự/liền kề: Đồng bộ 12±2cm (Bể ngầm/bể bơi đổ bơm 14±2cm)."
    },
    {
        "bill_no": "Bill 7. Spec",
        "title": "Chỉ dẫn kỹ thuật và thông tin quy cách vật tư bắt buộc trong BOQ",
        "key_rule": "Đào đắp phải ghi rõ cự ly vận chuyển và bãi đổ; Cọc ghi rõ chiều dài tổ hợp; Bê tông ghi rõ mác, đá, độ sụt, phụ gia; Thép ghi rõ giới hạn chảy CB300V/CB400V/CB500V."
    },
    {
        "bill_no": "Bill 8. BV, PS",
        "title": "Quy định về Bản vẽ phát hành, Shopdrawing & Nguyên tắc Phát sinh",
        "key_rule": "Bản vẽ HSMT phải là bản vẽ TKKT hoặc BVTC được duyệt. Nhà thầu thi công sai thiết kế tự chịu 100% chi phí đục phá khắc phục và không được tính phát sinh."
    }
]

VARIATION_ORDER_12_STEPS = [
    {"step": 1, "name": "Báo cáo phát sinh hiện trường", "form": "BM.01-QT01-XLPS", "sla": "1 - 2 ngày"},
    {"step": 2, "name": "Họp kiểm tra, đánh giá & xác nhận phát sinh tại hiện trường", "form": "BM.02-QT01-XLPS (Khẩn cấp: Chỉ thị công trường BM.05 trong 24h)", "sla": "2 - 4 ngày"},
    {"step": 3, "name": "Nhà thầu lập Hồ sơ đề xuất phát sinh (KL & đơn giá)", "form": "BM.03-QT01-XLPS & BM.04-QT01-XLPS", "sla": "2 ngày"},
    {"step": 4, "name": "BQLDA/QLXD kiểm tra hồ sơ & lập Tờ trình xin chủ trương", "form": "Tờ trình chủ trương PS", "sla": "2 ngày"},
    {"step": 5, "name": "Lãnh đạo Tập đoàn / Founder phê duyệt chủ trương phát sinh", "form": "Phê duyệt chủ trương", "sla": "2 ngày"},
    {"step": 6, "name": "Thông báo cho phép triển khai thi công hạng mục phát sinh", "form": "Văn bản triển khai", "sla": "1 ngày"},
    {"step": 7, "name": "Ban KTXD kiểm soát khối lượng & thẩm định giá trị phát sinh", "form": "BM01-KTXD CTGPS & BM02-KTXD CTGPS", "sla": "2 - 11 ngày"},
    {"step": 8, "name": "Đàm phán giá và điều khoản Phụ lục Hợp đồng với Nhà thầu", "form": "Biên bản đàm phán PLHĐ", "sla": "2 - 3 ngày"},
    {"step": 9, "name": "Trình phê duyệt giá trị sau đàm phán & dự thảo PLHĐ", "form": "Tờ trình duyệt PLHĐ", "sla": "2 ngày"},
    {"step": 10, "name": "Ký kết Phụ lục Hợp đồng chính thức", "form": "Phụ lục Hợp đồng", "sla": "2 ngày"},
    {"step": 11, "name": "Phát hành Phụ lục Hợp đồng cho các phòng ban", "form": "Phiếu phát hành", "sla": "0.5 ngày"},
    {"step": 12, "name": "Lưu trữ hồ sơ gốc và cập nhật ngân sách dự án", "form": "Hồ sơ lưu trữ", "sla": "Liên tục"}
]


# ==============================================================================
# 4. TRỤ CỘT 4: BỘ 17 BIỂU MẪU CHECKLIST HỒ SƠ CHẤT LƯỢNG QA/QC HIỆN TRƯỜNG
# Áp dụng cho: Phòng Quản lý Chất lượng QA/QC (DEPT_QAQC)
# ==============================================================================
QAQC_17_CHECKLIST_TEMPLATES = [
    {"stt": 1, "code": "1.BM-PD NTP", "name": "Biểu mẫu Phê duyệt Nhà thầu phụ thi công"},
    {"stt": 2, "code": "2.BM-PD NCC", "name": "Biểu mẫu Phê duyệt Nhà cung cấp vật tư, thiết bị"},
    {"stt": 3, "code": "3.BM-BBKT NCC", "name": "Biên bản kiểm tra năng lực thực tế Nhà cung cấp / Mỏ vật liệu / Trạm trộn"},
    {"stt": 4, "code": "4.BM-PD PTN", "name": "Biểu mẫu Kiểm tra & Phê duyệt Phòng thí nghiệm chuyên ngành xây dựng (LAS-XD)"},
    {"stt": 5, "code": "5.BM-PD TB", "name": "Biểu mẫu Phê duyệt Máy móc thiết bị thi công đưa vào công trường"},
    {"stt": 6, "code": "6.BM-BB BGMB", "name": "Biên bản bàn giao mặt bằng, tim mốc, cao độ chuẩn công trường"},
    {"stt": 7, "code": "7.BM-NTVL (P1)", "name": "Phiếu yêu cầu & Biên bản nghiệm thu vật liệu, thiết bị đầu vào trước khi đưa vào sử dụng"},
    {"stt": 8, "code": "8.BM-NTVL (P2)", "name": "Bảng tổng hợp theo dõi CO, CQ, chứng nhận hợp chuẩn/hợp quy vật tư đầu vào"},
    {"stt": 9, "code": "9.BM-NTCVXD (P1)", "name": "Phiếu yêu cầu nghiệm thu công việc xây dựng của Nhà thầu"},
    {"stt": 10, "code": "10.BM-NTCVXD (P2)", "name": "Biên bản nghiệm thu công việc xây dựng (BBNTCV)"},
    {"stt": 11, "code": "11.BM-BBKTCVTC", "name": "Biên bản kiểm tra công việc thi công hàng ngày tại hiện trường"},
    {"stt": 12, "code": "12.BM-BBLMTN", "name": "Biên bản lấy mẫu thí nghiệm tại hiện trường có sự chứng kiến các bên"},
    {"stt": 13, "code": "13.BM-BBXNCVTC", "name": "Biên bản xác nhận khối lượng công việc hoàn thành giai đoạn/hiện trường"},
    {"stt": 14, "code": "14.BM-BBNTHTGĐ", "name": "Biên bản nghiệm thu hoàn thành bộ phận công trình, giai đoạn thi công xây dựng"},
    {"stt": 15, "code": "15.BM-NKTC", "name": "Mẫu Nhật ký thi công xây dựng công trình chuẩn Tập đoàn"},
    {"stt": 16, "code": "16.BM-NKATLĐ", "name": "Mẫu Nhật ký An toàn lao động, Vệ sinh môi trường & PCCC"},
    {"stt": 17, "code": "17.BM-BBNTHT", "name": "Biên bản nghiệm thu hoàn thành hạng mục công trình / công trình đưa vào sử dụng"}
]


# ==============================================================================
# 5. TRỤ CỘT 5: QUY ĐỊNH TẠM ỨNG, THANH QUYẾT TOÁN (QĐ 122, QĐ 123 & CHECKLIST TQT)
# Áp dụng cho: Phòng Kiểm toán Thanh & Quyết toán (DEPT_SETTLEMENT)
# ==============================================================================
SETTLEMENT_CORPORATE_RULES = {
    "decisions": "Quyết định 122/QĐ-TGĐ & Quyết định 123/QĐ-TGĐ (Quy định Tạm ứng, Thanh quyết toán HĐ Xây dựng & Cung ứng)",
    "core_principles": [
        "Nguyên tắc 'Người làm có người kiểm tra': Mọi hồ sơ TQT bắt buộc qua 2 cấp (Chuyên viên kiểm tra chi tiết -> Trưởng bộ phận rà soát phê duyệt).",
        "Nguyên tắc 'Từ chối tiếp nhận nếu mắc trên 03 lỗi cơ bản' (3-Strike Rejection Rule): Không có danh mục hồ sơ; Tờ trình sai mẫu/số liệu; thiếu Báo cáo kiểm tra; Bảng tính không có chữ ký nháy từng trang; BB nghiệm thu/Shopdrawing/BVHC thiếu ngày tháng hoặc ghi đối tượng chung chung; thiếu CO/CQ/KQTN.",
        "SLA Phản hồi & Sửa lỗi: Bộ phận tiếp nhận phản hồi tối đa trong 24 giờ; đơn vị trình/nhà thầu hoàn thiện lại trong 02 ngày làm việc. Nếu bị trả lại từ lần thứ 2 trở lên phải phát hành Văn bản Cảnh báo năng lực lập HSTT của Nhà thầu.",
        "Tỷ lệ thẩm định khối lượng trọng yếu của Ban KTXD: (1) Thanh toán đợt khi lũy kế <= 70% giá trị HĐ: kiểm tra xác suất tối thiểu 50% giá trị các công tác chính; (2) Thanh toán đợt khi lũy kế > 70% giá trị HĐ: kiểm tra tối thiểu 80% giá trị các công tác chính; (3) Hồ sơ Quyết toán: thẩm định 100% khối lượng toàn bộ hợp đồng.",
        "Nguyên tắc Bảo vệ lợi ích Chủ đầu tư: Khi có sự sai khác số liệu giữa các tài liệu hoặc nhiều cách hiểu khác nhau, bắt buộc áp dụng giá trị MIN (nhỏ hơn) có lợi nhất cho Chủ đầu tư.",
        "Loại trừ vật tư thay đổi chưa duyệt: Mọi vật tư, thiết bị thay đổi chủng loại/quy cách/xuất xứ so với Hợp đồng mà chưa ký Phụ lục hợp đồng thì loại thẳng khỏi giá trị thanh toán đợt."
    ],
    "key_forms": [
        {"code": "BM01", "name": "Kế hoạch thanh toán định kỳ hàng tháng"},
        {"code": "BM05 / BM06.1", "name": "Báo cáo kiểm tra Hồ sơ thanh quyết toán của BQLDA / Ban QLXD"},
        {"code": "BM-07 / BM-14", "name": "Báo cáo thẩm định Hồ sơ thanh quyết toán của Ban Kinh tế Xây dựng (KTXD)"},
        {"code": "BM-16.1 / BM-16.2", "name": "Tờ trình Chủ tịch Điều hành / Founder phê duyệt Thanh toán (16.1) & Quyết toán (16.2)"},
        {"code": "BM17", "name": "Báo cáo tổng hợp theo dõi tình hình Thanh quyết toán toàn dự án"}
    ]
}


class CorporateSOPEngine:
    """
    Bộ máy tra cứu & áp dụng Quy trình, Quy chế, Biểu mẫu nội bộ Tập đoàn T&T
    """

    @classmethod
    def get_all_pillars_summary(cls) -> Dict[str, Any]:
        return {
            "source_directory": SOP_ROOT_DIR,
            "directory_exists": os.path.exists(SOP_ROOT_DIR),
            "pillars": [
                {
                    "id": "PILLAR_1_LEGAL",
                    "department": "DEPT_LEGAL",
                    "title": "Bộ 44 Hợp Đồng Mẫu Xây Dựng & Cung Ứng (QĐ 690 & QĐ 560)",
                    "regulations": ["QĐ 690/QĐ-TGĐ (30 mẫu HĐ Xây dựng & Tư vấn)", "QĐ 560/QĐ-TGĐ (14 mẫu HĐ Cung ứng Đợt 1 & 2)"],
                    "templates": list(STANDARD_CONTRACT_TEMPLATES.values()),
                    "rules": LEGAL_CORPORATE_RULES
                },
                {
                    "id": "PILLAR_2_BIDDING",
                    "department": "DEPT_BIDDING",
                    "title": "Quy Hoạch Gói Thầu, Quy Trình LCNT & 33 Mẫu HSMT Chuẩn (QĐ 419/420/421, QĐ 516/517, QĐ 458)",
                    "regulations": [
                        "QĐ 419/QĐ-TGĐ (Quy định LCNT Thi công xây lắp)",
                        "QĐ 420/QĐ-TGĐ (Quy định LCNT Tư vấn)",
                        "QĐ 421/QĐ-TGĐ (Quy chế Hội đồng xét thầu)",
                        "QĐ 516 & 517/QĐ-TGĐ (Quy định LCNT Cung ứng HHDV)",
                        "QĐ 458/QĐ-TGĐ (33 Bộ mẫu HSMT chuẩn hóa GĐ1 & GĐ2)"
                    ],
                    "package_groups": BIDDING_PACKAGE_GROUPS,
                    "lcnt_forms": BIDDING_LCNT_TEMPLATES,
                    "hsmt_templates": HSMT_STANDARD_TEMPLATES_QD458
                },
                {
                    "id": "PILLAR_3_QS_BOQ",
                    "department": "DEPT_QS",
                    "title": "Chuẩn Hóa HSMT 8 Bill Tiên Lượng & Quy Trình Xử Lý Phát Sinh 12 Bước (QT01-XLPS)",
                    "regulations": [
                        "Bộ khung 8 Bill Chuẩn hóa HSMT (Trần CPC 5%, Nguyên tắc MIN khối lượng, Độ sụt BTTP)",
                        "QT01-XLPS: Quy trình kiểm soát & phê duyệt phát sinh 12 bước (BM.01 -> BM.05)"
                    ],
                    "hsmt_8_bills": HSMT_8_BILLS_STANDARD,
                    "variation_12_steps": VARIATION_ORDER_12_STEPS
                },
                {
                    "id": "PILLAR_4_QAQC",
                    "department": "DEPT_QAQC",
                    "title": "Bộ 17 Biểu Mẫu Checklist Quản Lý Chất Lượng & Nghiệm Thu Hiện Trường",
                    "regulations": [
                        "Checklist 17 Biểu mẫu Quản lý chất lượng từ Phê duyệt NTP/NCC/LAS-XD đến Nghiệm thu hoàn thành",
                        "Bill 8 Chuẩn hóa HSMT: Quy định thẩm quyền phê duyệt Shopdrawing & Biện pháp thi công"
                    ],
                    "qaqc_17_forms": QAQC_17_CHECKLIST_TEMPLATES
                },
                {
                    "id": "PILLAR_5_SETTLEMENT",
                    "department": "DEPT_SETTLEMENT",
                    "title": "Quy Định Tạm Ứng, Thanh Quyết Toán & Kiểm Toán KTXD (QĐ 122 & QĐ 123)",
                    "regulations": [
                        "Quyết định 122/QĐ-TGĐ & Quyết định 123/QĐ-TGĐ (Quy định Tạm ứng, Thanh quyết toán)",
                        "Bộ Checklist Hồ sơ TQT & Mẫu Tờ trình CTĐH phê duyệt TQT (BM-16.1 / BM-16.2)"
                    ],
                    "settlement_rules": SETTLEMENT_CORPORATE_RULES["core_principles"],
                    "settlement_forms": SETTLEMENT_CORPORATE_RULES["key_forms"]
                }
            ]
        }

    @classmethod
    def recommend_contract_template(cls, contract_title: str, contract_value: float) -> Dict[str, Any]:
        """Tự động chọn mẫu Hợp đồng chuẩn theo QĐ 690/QĐ-TGĐ và QĐ 560/QĐ-TGĐ"""
        title_lower = contract_title.lower()
        if any(k in title_lower for k in ["cơ điện", "mep", "pccc", "điện nhẹ", "trạm biến áp", "điều hòa", "thang máy"]):
            selected = STANDARD_CONTRACT_TEMPLATES["CONSTRUCTION_MEP"]
        elif any(k in title_lower for k in ["nhôm kính", "mặt dựng", "facade"]):
            selected = STANDARD_CONTRACT_TEMPLATES["CONSTRUCTION_ALUMINUM_GLASS"]
        elif any(k in title_lower for k in ["nội thất", "đồ rời"]):
            selected = STANDARD_CONTRACT_TEMPLATES["CONSTRUCTION_INTERIOR"]
        elif any(k in title_lower for k in ["tư vấn", "thiết kế", "giám sát", "khảo sát", "thẩm tra"]):
            selected = STANDARD_CONTRACT_TEMPLATES["CONSULTANCY_CONTRACTS"]
        elif any(k in title_lower for k in ["cung cấp", "mua sắm", "vật tư"]):
            selected = STANDARD_CONTRACT_TEMPLATES["SUPPLY_CONTRACTS"]
        elif contract_value >= 3_000_000_000:
            selected = STANDARD_CONTRACT_TEMPLATES["CONSTRUCTION_OVER_3B"]
        else:
            selected = STANDARD_CONTRACT_TEMPLATES["CONSTRUCTION_UNDER_3B"]

        return {
            "primary_template": selected,
            "mandatory_attachment": STANDARD_CONTRACT_TEMPLATES["NDA_ANTI_CORRUPTION"],
            "bond_validity_rule": "Hiệu lực Bảo lãnh thực hiện HĐ & Bảo lãnh tạm ứng >= Thời gian thực hiện HĐ + 30 ngày (QĐ 122/123)"
        }

    @classmethod
    def recommend_bidding_templates(cls, package_name: str, package_type: str) -> Dict[str, Any]:
        """Tự động ánh xạ gói thầu với mẫu HSMT chuẩn QĐ 458 và quy trình LCNT QĐ 419/420/516"""
        name_lower = package_name.lower()
        hsmt_code = "BM12"
        if any(k in name_lower for k in ["cọc", "nền móng", "tường vây"]):
            hsmt_code = "BM16"
        elif any(k in name_lower for k in ["trạm biến áp"]):
            hsmt_code = "BM32"
        elif any(k in name_lower for k in ["máy phát điện"]):
            hsmt_code = "BM33"
        elif any(k in name_lower for k in ["thang máy"]):
            hsmt_code = "BM35"
        elif any(k in name_lower for k in ["điều hòa", "hvac", "thông gió"]):
            hsmt_code = "BM40"
        elif any(k in name_lower for k in ["pccc", "chữa cháy"]):
            hsmt_code = "BM21"
        elif any(k in name_lower for k in ["cơ điện", "mep"]):
            hsmt_code = "BM13"
        elif any(k in name_lower for k in ["nhôm kính", "mặt dựng"]):
            hsmt_code = "BM20/28"
        elif any(k in name_lower for k in ["cây xanh", "cảnh quan"]):
            hsmt_code = "BM41"

        pkg_type_up = package_type.upper()
        if pkg_type_up == "CONSULTANCY":
            gov_decision = "Quyết định 420/QĐ-TGĐ (Quy định LCNT Tư vấn) & QĐ 421/QĐ-TGĐ (Hội đồng xét thầu)"
        elif pkg_type_up == "GOODS":
            gov_decision = "Quyết định 516/QĐ-TGĐ & 517/QĐ-TGĐ (Quy định LCNT Cung ứng Hàng hóa Dịch vụ)"
        else:
            gov_decision = "Quyết định 419/QĐ-TGĐ (Quy định LCNT Thi công xây lắp) & QĐ 421/QĐ-TGĐ (Hội đồng xét thầu)"

        return {
            "governing_internal_decision": gov_decision,
            "recommended_hsmt_code": hsmt_code,
            "recommended_hsmt_name": HSMT_STANDARD_TEMPLATES_QD458.get(hsmt_code, HSMT_STANDARD_TEMPLATES_QD458["BM12"]),
            "clarification_limit_rule": "BM04-BCDGKT: Nhà thầu chỉ được phép làm rõ Hồ sơ đề xuất Kỹ thuật tối đa 01 lần.",
            "mandatory_lcnt_forms": BIDDING_LCNT_TEMPLATES
        }

    @classmethod
    def get_ktxd_audit_scope(cls, contract_val: float, cumulative_val: float, is_final_settlement: bool = False) -> Dict[str, Any]:
        """Xác định tỷ lệ thẩm định khối lượng trọng yếu của Ban KTXD theo QĐ 122/123"""
        ratio = (cumulative_val / contract_val * 100.0) if contract_val > 0 else 0.0
        if is_final_settlement:
            return {
                "stage": "QUYẾT TOÁN HỢP ĐỒNG",
                "cumulative_ratio_percent": round(ratio, 2),
                "required_ktxd_audit_percent": 100,
                "rule_description": "Thẩm định chi tiết 100% khối lượng toàn bộ hợp đồng (Quy định TQT QĐ 122/123)",
                "submission_form": "BM-16.2 (Tờ trình Chủ tịch Điều hành phê duyệt Quyết toán)"
            }
        elif ratio <= 70.0:
            return {
                "stage": "THANH TOÁN ĐỢT (Lũy kế <= 70% giá trị HĐ)",
                "cumulative_ratio_percent": round(ratio, 2),
                "required_ktxd_audit_percent": 50,
                "rule_description": "Ban KTXD thẩm định xác suất các công tác chính chiếm tối thiểu 50% giá trị đề nghị thanh toán đợt (QĐ 122/123)",
                "submission_form": "BM-16.1 (Tờ trình Chủ tịch Điều hành phê duyệt Thanh toán đợt)"
            }
        else:
            return {
                "stage": "THANH TOÁN ĐỢT (Lũy kế > 70% giá trị HĐ)",
                "cumulative_ratio_percent": round(ratio, 2),
                "required_ktxd_audit_percent": 80,
                "rule_description": "Ban KTXD thẩm định chi tiết các công tác chính chiếm tối thiểu 80% giá trị đề nghị thanh toán đợt (QĐ 122/123)",
                "submission_form": "BM-16.1 (Tờ trình Chủ tịch Điều hành phê duyệt Thanh toán đợt)"
            }


corporate_sop_engine = CorporateSOPEngine()
