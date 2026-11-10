# -*- coding: utf-8 -*-
"""
SAFEGUARDS: Zero-Hallucination Protocol & Construction Blind-Spot Controller
Bo quy tac chong bia dat so lieu, kiem soat diem mu phap ly va rang buoc chat che.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

class ZeroHallucinationError(Exception):
    """Loi khi Agent co dau hieu tu bia so lieu hoac thieu can cu nguon."""
    pass

class ConstructionSafeguards:
    """
    He thong chan loc va kiem tra cheo 3 chieu (3-Way Verification)
    1. Can cu Phap ly (Dieu, Khoan, So hieu, Ngay hieu luc)
    2. Nguon du lieu vat ly (File goc, Sheet goc, O tinh goc, Ban ve CAD)
    3. Tinh logic toan hoc (Khong hardcode so, khong lech tong cong)
    """

    # Moc thoi gian chuyen tiep phap luat then chot nam 2026
    TRANSITION_DATES = {
        "ND_210_CONTRACTS": datetime(2026, 7, 1),   # Hieu luc Nghi dinh 210/2026/ND-CP
        "ND_349_BIDDING": datetime(2026, 9, 9),      # Hieu luc Nghi dinh 349/2026/ND-CP
        "TT_09_NORMS": datetime(2024, 10, 15)       # Hieu luc Thong tu 09/2024/TT-BXD
    }

    # Nguong bat buoc chuyen cap Founder phe duyet (Human-in-the-Loop)
    THRESHOLDS = {
        "PAYMENT_APPROVAL_VND": 500_000_000,         # Tren 500 trieu phai Founder ky
        "ADVANCE_GUARANTEE_VND": 1_000_000_000,      # Tam ung > 1 ty bat buoc bao lanh ngan hang
        "MAX_ADVANCE_PERCENT": 30.0,                 # Tran tam ung toi da 30% theo ND 210
        "VARIATION_PERCENT_LIMIT": 5.0,              # Phat sinh > 5% bat buoc lap phu luc HD
        "BID_OUTLIER_PERCENT": 30.0                  # Bao gia lech > 30% so voi trung binh phai loai bo (ND 349)
    }

    @classmethod
    def audit_contract_timing(cls, contract_date_str: str) -> Dict[str, Any]:
        """
        Diem mu 1: Kiem tra thoi diem ky hop dong de ap dung dung Nghi dinh chuyen tiep.
        Tranh tinh trang ap NĐ 210/2026 cho hop dong ky truoc 01/07/2026.
        """
        try:
            contract_date = datetime.strptime(contract_date_str.strip(), "%Y-%m-%d")
        except ValueError:
            try:
                contract_date = datetime.strptime(contract_date_str.strip(), "%d/%m/%Y")
            except ValueError:
                return {
                    "valid": False,
                    "error": f"Dinh dang ngay thang khong hop le: {contract_date_str}. Phai dung YYYY-MM-DD hoac DD/MM/YYYY."
                }

        is_after_210 = contract_date >= cls.TRANSITION_DATES["ND_210_CONTRACTS"]
        applicable_decree = "Nghị định 210/2026/NĐ-CP" if is_after_210 else "Nghị định 37/2015/NĐ-CP & NĐ 50/2021/NĐ-CP"

        return {
            "valid": True,
            "contract_date": contract_date.strftime("%d/%m/%Y"),
            "is_governed_by_210": is_after_210,
            "applicable_decree": applicable_decree,
            "advance_cap_percent": 30.0 if is_after_210 else 50.0,
            "advance_guarantee_required_over": 1_000_000_000 if is_after_210 else None,
            "settlement_deadline_days": 60 if is_after_210 else 90
        }

    @classmethod
    def audit_advance_payment(cls, contract_value: float, requested_advance: float, has_guarantee: bool) -> Dict[str, Any]:
        """
        Kiem tra gioi han tam ung va bat buoc bao lanh ngan hang theo ND 210/2026.
        """
        if contract_value <= 0:
            return {"valid": False, "reason": "Giá trị hợp đồng phải lớn hơn 0."}

        advance_percent = (requested_advance / contract_value) * 100.0
        violations = []
        warnings = []

        if advance_percent > cls.THRESHOLDS["MAX_ADVANCE_PERCENT"]:
            violations.append(
                f"Vi phạm trần tạm ứng: Mức yêu cầu {advance_percent:.1f}% vượt quá trần quy định 30% giá hợp đồng "
                "(Khoản 2 Điều 18 Nghị định 210/2026/NĐ-CP)."
            )

        if requested_advance > cls.THRESHOLDS["ADVANCE_GUARANTEE_VND"] and not has_guarantee:
            violations.append(
                f"Thiếu Bảo lãnh tạm ứng: Tạm ứng {requested_advance:,.0f} VNĐ (vượt quá 01 tỷ đồng) bắt buộc phải "
                "có Bảo lãnh tiền tạm ứng hợp pháp từ ngân hàng thương mại (Nghị định 210/2026/NĐ-CP)."
            )

        return {
            "valid": len(violations) == 0,
            "advance_percent": round(advance_percent, 2),
            "requested_advance": requested_advance,
            "violations": violations,
            "warnings": warnings,
            "requires_founder_approval": requested_advance >= cls.THRESHOLDS["PAYMENT_APPROVAL_VND"]
        }

    @classmethod
    def audit_bidding_quotes(cls, quotes: List[Dict[str, Any]], tender_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Diem mu 2: Kiem tra gia goi thau va loc bo bao gia bat thuong lech > 30% theo ND 349/2026.
        """
        if not quotes or len(quotes) < 3:
            return {
                "valid": False,
                "error": "Cần tối thiểu 03 báo giá hợp lệ từ các nhà cung cấp độc lập để xác định giá gói thầu."
            }

        valid_prices = [q["price"] for q in quotes if q.get("price", 0) > 0]
        avg_price = sum(valid_prices) / len(valid_prices)

        filtered_quotes = []
        excluded_quotes = []

        for q in quotes:
            p = q.get("price", 0)
            diff_percent = abs(p - avg_price) / avg_price * 100.0
            if diff_percent > cls.THRESHOLDS["BID_OUTLIER_PERCENT"]:
                excluded_quotes.append({
                    "supplier": q.get("supplier", "Ẩn danh"),
                    "price": p,
                    "diff_percent": round(diff_percent, 2),
                    "reason": f"Chênh lệch {diff_percent:.1f}% (> 30%) so với giá bình quân - Bị loại trừ theo Nghị định 349/2026/NĐ-CP."
                })
            else:
                filtered_quotes.append(q)

        new_avg = sum([q["price"] for q in filtered_quotes]) / len(filtered_quotes) if filtered_quotes else 0

        return {
            "valid": len(filtered_quotes) >= 2,
            "original_count": len(quotes),
            "excluded_count": len(excluded_quotes),
            "excluded_quotes": excluded_quotes,
            "accepted_quotes": filtered_quotes,
            "benchmark_package_price": round(new_avg, 0)
        }

    @classmethod
    def verify_source_attribution(cls, data_dict: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        GIAO THUC CAM CHE CHAO: Moi so lieu phai chi ro file nguon va toa do du lieu.
        """
        missing_sources = []
        for field in required_fields:
            src = data_dict.get(f"{field}_source")
            val = data_dict.get(field)
            if val is not None and not src:
                missing_sources.append(field)

        if missing_sources:
            return {
                "passed": False,
                "error": f"Phát hiện số liệu thiếu căn cứ nguồn gốc: {missing_sources}. "
                         "Yêu cầu Agent không tự suy diễn hoặc bịa số liệu."
            }

        return {"passed": True}
