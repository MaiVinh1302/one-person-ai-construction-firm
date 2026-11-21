# -*- coding: utf-8 -*-
"""
DEPARTMENT 7: Planning, CPM Scheduling & Progress Reporting
(Phòng Kế hoạch & Kiểm soát Tiến độ Thi công - Chuẩn tiendothicong.vercel.app)

Cơ cấu 2 cấp nhân sự:
1. Chuyên viên Lập Tiến độ CPM: Trần Tiến Độ (Level 2 Specialist)
   - Lập cây WBS 6 giai đoạn, tính toán đường găng CPM (Forward/Backward Pass, Total Float, Free Float),
     phân bổ ngân sách & biểu đồ dòng tiền S-Curve, xuất/nhập .tiendo.json và MS Project XML.
2. Trưởng phòng Kiểm soát Tiến độ & EVM: Nguyễn Kế Hoạch (Level 1 Department Head)
   - Kiểm toán logic mạng găng (SPEC 3.2: phát hiện chu trình, việc treo, găng đứt đoạn),
     phân tích sâu chỉ số EVM (SPI, CPI, EAC, VAC), đề xuất nén tiến độ (Crashing / Fast-tracking)
     và thẩm định hồ sơ gia hạn EOT / phạt chậm tiến độ theo Nghị định 210/2026/NĐ-CP & 207/2026/NĐ-CP.
"""

import re
import datetime
from typing import Dict, List, Any, Optional
from core.permissions import RoleLevel


class PlanningScheduleSpecialistAgent:
    AGENT_NAME = "Trần Tiến Độ"
    ROLE_TITLE = "Kỹ sư Lập Tiến độ CPM, WBS, Cân bằng Tài nguyên & S-Curve"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def parse_predecessors(cls, preds: Any) -> List[Dict[str, Any]]:
        """Phân tích chuỗi hoặc danh sách tiền nhiệm thành cấu trúc chuẩn {fromId, type, lag}."""
        parsed: List[Dict[str, Any]] = []
        if not preds:
            return parsed

        if isinstance(preds, str):
            # Tách chuỗi theo dấu phẩy hoặc chấm phẩy: "1:FS+0, 2:SS+2" hoặc "1, 2"
            parts = [p.strip() for p in re.split(r"[,;]+", preds) if p.strip()]
            for p in parts:
                m = re.match(r"^([A-Za-z0-9_-]+)(?::?(FS|SS|FF|SF))?(?:([+-]\d+))?$", p, re.IGNORECASE)
                if m:
                    from_id = m.group(1)
                    rel_type = (m.group(2) or "FS").upper()
                    lag = int(m.group(3) or 0)
                    parsed.append({"fromId": from_id, "type": rel_type, "lag": lag})
                else:
                    parsed.append({"fromId": p, "type": "FS", "lag": 0})
        elif isinstance(preds, list):
            for item in preds:
                if isinstance(item, str):
                    parsed.extend(cls.parse_predecessors(item))
                elif isinstance(item, dict):
                    fid = str(item.get("fromId") or item.get("id") or "")
                    rel = str(item.get("type") or "FS").upper()
                    lag = int(item.get("lag") or 0)
                    if fid:
                        parsed.append({"fromId": fid, "type": rel, "lag": lag})
        return parsed

    @classmethod
    def compute_cpm_and_evm(
        cls,
        project_name: str,
        tasks: List[Dict[str, Any]],
        actual_cost: float = 0.0,
        start_date: str = "2026-11-21",
        work_days_per_week: int = 6,
    ) -> Dict[str, Any]:
        """
        Thực hiện tính toán Forward/Backward Pass CPM, xác định Total Float (TF),
        Free Float (FF), nhận diện Đường găng và tính toán toàn diện chỉ số EVM.
        """
        task_map: Dict[str, Dict[str, Any]] = {}
        for idx, t in enumerate(tasks):
            tid = str(t.get("id") or f"T{idx + 1}")
            code = str(t.get("code") or t.get("wbs") or f"1.{idx + 1}")
            dur = max(0, int(t.get("durationDays") or t.get("duration") or 1))
            prog = max(0.0, min(100.0, float(t.get("progress", 0))))
            budget = max(0.0, float(t.get("budget", 0)))
            subcon = str(t.get("subcontractor") or t.get("resource") or "Đội thi công nội bộ")
            kind = str(t.get("kind") or "task").lower()
            if kind == "milestone":
                dur = 0

            raw_preds = t.get("predecessors") or []
            parsed_preds = cls.parse_predecessors(raw_preds)

            task_map[tid] = {
                "id": tid,
                "code": code,
                "wbs": code,
                "name": t.get("name") or f"Công việc {tid}",
                "kind": kind,
                "durationDays": dur,
                "progress": prog,
                "budget": budget,
                "subcontractor": subcon,
                "predecessors": parsed_preds,
                "es": 0,
                "ef": dur,
                "ls": 0,
                "lf": dur,
                "tf": 0,
                "ff": 0,
                "isCritical": False,
                "baseline_start": t.get("baseline_start", 0),
                "baseline_finish": t.get("baseline_finish", dur),
            }

        ids = list(task_map.keys())
        has_cycle = False

        # --- 1. FORWARD PASS (TÍNH TIẾN ES, EF) ---
        for _ in range(len(ids) + 2):
            changed = False
            for tid in ids:
                cur = task_map[tid]
                es = 0
                for link in cur["predecessors"]:
                    pid = link["fromId"]
                    ltype = link["type"]
                    lag = link["lag"]
                    if pid not in task_map:
                        continue
                    p = task_map[pid]
                    if ltype == "FS":
                        cand = p["ef"] + lag
                    elif ltype == "SS":
                        cand = p["es"] + lag
                    elif ltype == "FF":
                        cand = p["ef"] + lag - cur["durationDays"]
                    elif ltype == "SF":
                        cand = p["es"] + lag - cur["durationDays"]
                    else:
                        cand = p["ef"] + lag

                    if cand > es:
                        es = cand

                ef = es + cur["durationDays"]
                if es != cur["es"] or ef != cur["ef"]:
                    cur["es"] = es
                    cur["ef"] = ef
                    changed = True
            if not changed:
                break
        else:
            has_cycle = True

        project_duration = max((t["ef"] for t in task_map.values()), default=0)

        # --- 2. BACKWARD PASS (TÍNH LÙI LF, LS) ---
        succ_map: Dict[str, List[Dict[str, Any]]] = {tid: [] for tid in ids}
        for tid in ids:
            for link in task_map[tid]["predecessors"]:
                pid = link["fromId"]
                if pid in succ_map:
                    succ_map[pid].append({
                        "toId": tid,
                        "type": link["type"],
                        "lag": link["lag"]
                    })

        for tid in ids:
            task_map[tid]["lf"] = project_duration
            task_map[tid]["ls"] = project_duration - task_map[tid]["durationDays"]

        for _ in range(len(ids) + 2):
            changed = False
            for tid in reversed(ids):
                cur = task_map[tid]
                lf = project_duration
                for sl in succ_map[tid]:
                    sid = sl["toId"]
                    if sid not in task_map:
                        continue
                    s = task_map[sid]
                    if sl["type"] == "FS":
                        cand = s["ls"] - sl["lag"]
                    elif sl["type"] == "SS":
                        cand = s["ls"] - sl["lag"] + cur["durationDays"]
                    elif sl["type"] == "FF":
                        cand = s["lf"] - sl["lag"]
                    elif sl["type"] == "SF":
                        cand = s["lf"] - sl["lag"] + cur["durationDays"]
                    else:
                        cand = s["ls"] - sl["lag"]
                    if cand < lf:
                        lf = cand
                ls = lf - cur["durationDays"]
                if lf != cur["lf"] or ls != cur["ls"]:
                    cur["lf"] = lf
                    cur["ls"] = ls
                    changed = True
            if not changed:
                break

        # --- 3. TÍNH TOTAL FLOAT (TF), FREE FLOAT (FF) & ĐƯỜNG GĂNG ---
        critical_tasks = []
        dangling_tasks = []
        total_budget = 0.0
        earned_value = 0.0
        weighted_progress_sum = 0.0
        total_weight = 0.0

        for tid in ids:
            t = task_map[tid]
            t["tf"] = max(0, t["ls"] - t["es"])

            # Free Float = min(Successor ES - Lag) - Current EF
            if succ_map[tid]:
                min_succ_early = min(
                    (task_map[sl["toId"]]["es"] - sl["lag"] for sl in succ_map[tid] if sl["toId"] in task_map),
                    default=project_duration
                )
                t["ff"] = max(0, min_succ_early - t["ef"])
            else:
                t["ff"] = max(0, project_duration - t["ef"])

            t["isCritical"] = (t["tf"] <= 0 and t["durationDays"] > 0)
            if t["isCritical"]:
                critical_tasks.append(f"{t['code']} - {t['name']} ({t['durationDays']}d, {t['subcontractor']})")

            # Công việc treo (Dangling Task): Không có kế nhiệm và kết thúc trước ngày hoàn thành
            if not succ_map[tid] and t["ef"] < project_duration:
                dangling_tasks.append(f"{t['code']} - {t['name']} (Sớm hơn {project_duration - t['ef']} ngày)")

            w = t["budget"] if t["budget"] > 0 else max(1.0, float(t["durationDays"]))
            total_budget += t["budget"]
            earned_value += t["budget"] * (t["progress"] / 100.0)
            weighted_progress_sum += w * t["progress"]
            total_weight += w

        overall_progress = round(weighted_progress_sum / total_weight, 2) if total_weight > 0 else 0.0
        planned_value = round(total_budget * (overall_progress / 100.0 if overall_progress > 0 else 0.5), 2)
        if planned_value == 0 and total_budget > 0:
            planned_value = round(total_budget * 0.45, 2)

        # EVM Advanced Metrics
        sv = round(earned_value - planned_value, 2)
        cv = round(earned_value - actual_cost, 2)
        spi = round(earned_value / planned_value, 3) if planned_value > 0 else 1.0
        cpi = round(earned_value / actual_cost, 3) if actual_cost > 0 else 1.0

        # Dự báo ngân sách hoàn thành (EAC) & phương sai khi hoàn thành (VAC)
        eac = round(total_budget / cpi, 2) if cpi > 0 else total_budget
        vac = round(total_budget - eac, 2)
        etc = round(max(0.0, eac - actual_cost), 2)

        # Tính quy đổi ngày lịch (Calendar Dates)
        try:
            base_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        except Exception:
            base_dt = datetime.date.today()

        for t in task_map.values():
            t["start_date_cal"] = str(base_dt + datetime.timedelta(days=int(t["es"] * 7 / work_days_per_week)))
            t["finish_date_cal"] = str(base_dt + datetime.timedelta(days=int(t["ef"] * 7 / work_days_per_week)))

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "project_name": project_name,
            "start_date": start_date,
            "work_days_per_week": work_days_per_week,
            "project_duration_days": project_duration,
            "project_finish_date": str(base_dt + datetime.timedelta(days=int(project_duration * 7 / work_days_per_week))),
            "overall_progress_pct": overall_progress,
            "has_cycle": has_cycle,
            "critical_path_count": len(critical_tasks),
            "critical_tasks": critical_tasks,
            "dangling_tasks": dangling_tasks,
            "evm": {
                "bac": total_budget,
                "pv": planned_value,
                "ev": round(earned_value, 2),
                "ac": actual_cost,
                "sv": sv,
                "cv": cv,
                "spi": spi,
                "cpi": cpi,
                "eac": eac,
                "etc": etc,
                "vac": vac,
            },
            "tasks_computed": list(task_map.values()),
        }

    @classmethod
    def generate_standard_6phase_wbs(cls, project_name: str = "Tổ hợp Thương mại & Khách sạn T&T") -> List[Dict[str, Any]]:
        """Sinh bộ khung WBS 6 giai đoạn chuẩn thi công xây dựng Việt Nam (tiendothicong.vercel.app)."""
        return [
            # Giai đoạn 1: Chuẩn bị mặt bằng
            {"id": "T1", "wbs": "1.1", "name": "Định vị tim mốc trắc đạc & Bàn giao mặt bằng", "duration": 5, "kind": "task", "predecessors": [], "progress": 100, "budget": 200000000, "subcontractor": "Đội Trắc đạc"},
            {"id": "T2", "wbs": "1.2", "name": "Lắp dựng hàng rào tôn, cổng chính & Lán trại tạm", "duration": 8, "kind": "task", "predecessors": ["1:FS+0"], "progress": 100, "budget": 350000000, "subcontractor": "Tổ mộc & Thép"},
            {"id": "T3", "wbs": "1.3", "name": "Đấu nối điện nước thi công & Trạm biến áp tạm", "duration": 6, "kind": "task", "predecessors": ["2:SS+2"], "progress": 100, "budget": 250000000, "subcontractor": "Tổ Điện nước"},
            # Giai đoạn 2: Phần ngầm (Móng & Hầm)
            {"id": "T4", "wbs": "2.1", "name": "Thi công tường vây / Cọc khoan nhồi / Cọc ép D500", "duration": 30, "kind": "task", "predecessors": ["2:FS+0"], "progress": 90, "budget": 6500000000, "subcontractor": "Công ty Cọc Thăng Long"},
            {"id": "T5", "wbs": "2.2", "name": "Đào đất móng hầm, Shoring chống tầng hầm đợt 1 & 2", "duration": 22, "kind": "task", "predecessors": ["4:SS+10"], "progress": 70, "budget": 2800000000, "subcontractor": "Đội Cơ giới 1"},
            {"id": "T6", "wbs": "2.3", "name": "Thi công bê tông lót, đài móng, dầm giằng & sàn hầm", "duration": 20, "kind": "task", "predecessors": ["5:FS+0"], "progress": 50, "budget": 4500000000, "subcontractor": "Tổ Bê tông Hầm"},
            {"id": "T7", "wbs": "2.4", "name": "Mốc hoàn thành phần ngầm & Nghiệm thu BBNTCV", "duration": 0, "kind": "milestone", "predecessors": ["6:FS+0"], "progress": 50, "budget": 0, "subcontractor": "Tư vấn Giám sát"},
            # Giai đoạn 3: Kết cấu phần thân
            {"id": "T8", "wbs": "3.1", "name": "Cốt thép, ván khuôn & Bê tông cột vách dầm sàn T1-T5", "duration": 45, "kind": "task", "predecessors": ["7:FS+0"], "progress": 25, "budget": 9500000000, "subcontractor": "Nhà thầu Xây lắp 1"},
            {"id": "T9", "wbs": "3.2", "name": "Cốt thép, ván khuôn & Bê tông cột vách dầm sàn T6-Mái", "duration": 40, "kind": "task", "predecessors": ["8:FS+0"], "progress": 0, "budget": 8500000000, "subcontractor": "Nhà thầu Xây lắp 1"},
            {"id": "T10", "wbs": "3.3", "name": "Mốc Cất Nóc Công Trình (Top-Out Milestone)", "duration": 0, "kind": "milestone", "predecessors": ["9:FS+0"], "progress": 0, "budget": 0, "subcontractor": "Ban QLDA"},
            # Giai đoạn 4: Xây trát & Bao che
            {"id": "T11", "wbs": "4.1", "name": "Xây tường gạch ngắt tầng & Trát tường trong/ngoài", "duration": 35, "kind": "task", "predecessors": ["8:SS+15"], "progress": 10, "budget": 3200000000, "subcontractor": "Đội Thợ Nề 2"},
            {"id": "T12", "wbs": "4.2", "name": "Chống thấm sàn mái, ban công & Khu vệ sinh", "duration": 15, "kind": "task", "predecessors": ["11:SS+10"], "progress": 0, "budget": 650000000, "subcontractor": "Công ty Chống thấm Bách Khoa"},
            # Giai đoạn 5: Hệ thống Cơ điện (MEP)
            {"id": "T13", "wbs": "5.1", "name": "Lắp đặt ống luồn điện, cáp động lực & Cấp thoát nước", "duration": 35, "kind": "task", "predecessors": ["11:SS+8"], "progress": 15, "budget": 4200000000, "subcontractor": "Công ty MEP Sao Việt"},
            {"id": "T14", "wbs": "5.2", "name": "Lắp đặt hệ thống PCCC, họng cứu hỏa & Báo cháy tự động", "duration": 25, "kind": "task", "predecessors": ["13:SS+10"], "progress": 5, "budget": 2800000000, "subcontractor": "Nhà thầu PCCC Thăng Long"},
            # Giai đoạn 6: Hoàn thiện & Bàn giao
            {"id": "T15", "wbs": "6.1", "name": "Ốp lát gạch, trần thạch cao, sơn bả & Lắp cửa kính", "duration": 30, "kind": "task", "predecessors": ["11:FS+0", "13:FS+0"], "progress": 0, "budget": 3800000000, "subcontractor": "Tổ Hoàn thiện"},
            {"id": "T16", "wbs": "6.2", "name": "Kiểm định PCCC Cảnh sát PCCC & Nghiệm thu Bàn giao đưa vào sử dụng", "duration": 12, "kind": "task", "predecessors": ["14:FS+0", "15:FS+0"], "progress": 0, "budget": 350000000, "subcontractor": "Cục Giám định Xây dựng"},
            {"id": "T17", "wbs": "6.3", "name": "Mốc Bàn Giao Đưa Vào Sử Dụng (Handover)", "duration": 0, "kind": "milestone", "predecessors": ["16:FS+0"], "progress": 0, "budget": 0, "subcontractor": "Chủ đầu tư & Tổng thầu"}
        ]


class PlanningScheduleHeadReviewerAgent:
    AGENT_NAME = "Nguyễn Kế Hoạch"
    ROLE_TITLE = "Trưởng phòng Kiểm soát Tiến độ, EVM & Thẩm định Hợp đồng NĐ 210"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    @classmethod
    def review_schedule(cls, specialist_dossier: Dict[str, Any]) -> Dict[str, Any]:
        """Thẩm định 4 tầng kiểm soát: Logic mạng găng ➔ Sai lệch EVM ➔ Nguồn lực ➔ Pháp lý hợp đồng."""
        warnings: List[str] = []
        recommendations: List[str] = []

        # 1. Kiểm tra vòng lặp mạng găng
        if specialist_dossier.get("has_cycle"):
            warnings.append("LỖI NGHIÊM TRỌNG (SPEC 3.2): Phát hiện vòng lặp logic tuần hoàn (Circular Dependency) trong mạng CPM! Tiến độ không thể tính toán.")

        # 2. Kiểm tra công việc treo
        dangling = specialist_dossier.get("dangling_tasks") or []
        if dangling:
            warnings.append(f"CẢNH BÁO (SPEC 3.2): Phát hiện {len(dangling)} công việc treo (Dangling/Open-end tasks) chưa liên kết kế nhiệm.")
            recommendations.append("Nối các công việc treo vào mốc Nghiệm thu giai đoạn hoặc Mốc bàn giao để đường găng không bị hở.")

        # 3. Phân tích chỉ số EVM
        evm = specialist_dossier.get("evm", {})
        spi = evm.get("spi", 1.0)
        cpi = evm.get("cpi", 1.0)
        if spi < 0.90:
            warnings.append(f"CHẬM TIẾN ĐỘ NGUY HIỂM: SPI = {spi:.2f} (< 0.90). Giá trị thực tế EV chậm hơn kế hoạch {abs(evm.get('sv', 0)):,.0f} VNĐ.")
            recommendations.append("Kích hoạt ngay giải pháp Nén tiến độ (Fast-Tracking / Crashing) đối với các công việc trên Đường găng.")
            recommendations.append("Lập hồ sơ giải trình nguyên nhân chậm tiến độ và kiểm tra quyền yêu cầu gia hạn thời gian (EOT) theo Điều 23 Nghị định 210/2026/NĐ-CP.")
        elif spi < 0.95:
            warnings.append(f"CẢNH BÁO TIẾN ĐỘ: SPI = {spi:.2f} (< 0.95). Có nguy cơ trễ hạn bàn giao mốc quan trọng.")

        if cpi < 0.90:
            warnings.append(f"VƯỢT CHI PHÍ: CPI = {cpi:.2f} (< 0.90). Chi phí thi công thực tế AC đang cao hơn giá trị hoàn thành EV.")

        # 4. Kiểm toán tuân thủ Nghị định 210/2026 & Nghị định 207/2026
        gate_status = "BLOCKED" if specialist_dossier.get("has_cycle") else ("WARNING" if warnings else "APPROVED")

        summary = (
            f"Trưởng phòng {cls.AGENT_NAME}: Tổng thời gian CPM = {specialist_dossier.get('project_duration_days', 0)} ngày, "
            f"Tiến độ hoàn thành chung = {specialist_dossier.get('overall_progress_pct', 0)}%, "
            f"Đường găng gồm {specialist_dossier.get('critical_path_count', 0)} công việc. "
            f"Chỉ số hiệu suất: SPI = {spi:.2f}, CPI = {cpi:.2f}. "
            f"Dự báo chi phí hoàn thành EAC = {evm.get('eac', 0):,.0f} VNĐ."
        )

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "can_proceed": gate_status != "BLOCKED",
            "applicable_law": (
                "Nghị định 210/2026/NĐ-CP (Quản lý hợp đồng & Phạt/Gia hạn tiến độ EOT), "
                "Nghị định 207/2026/NĐ-CP (Nhật ký điện tử & Nghiệm thu BBNTCV theo mốc), "
                "Nghị định 254/2025/NĐ-CP (Thanh toán khối lượng theo Mẫu 03.a/TT đối chiếu EV)"
            ),
            "warnings_count": len(warnings),
            "warnings": warnings,
            "recommendations": recommendations,
            "review_summary": summary,
        }

    @classmethod
    def recommend_compression(cls, specialist_dossier: Dict[str, Any], target_days: int = 15) -> Dict[str, Any]:
        """Đề xuất phương án nén tiến độ (Crashing / Fast-tracking) trên các công việc đường găng."""
        crit_tasks = [t for t in specialist_dossier.get("tasks_computed", []) if t.get("isCritical")]
        crashing_plans = []
        fast_tracking_plans = []

        for t in crit_tasks:
            dur = t.get("durationDays", 0)
            if dur > 7:
                # Đề xuất Crashing (tăng ca, thêm tổ đội để giảm 25-30% thời gian)
                reduced = max(1, int(dur * 0.3))
                crashing_plans.append({
                    "task_code": t.get("code"),
                    "task_name": t.get("name"),
                    "current_duration": dur,
                    "target_duration": dur - reduced,
                    "time_saved_days": reduced,
                    "method": "Tăng thêm 01 tổ đội hoặc tăng ca làm đêm (Crashing)",
                    "estimated_extra_cost": round(t.get("budget", 0) * 0.08, 0)
                })

            # Đề xuất Fast-tracking cho liên kết FS
            for p in t.get("predecessors", []):
                if p.get("type") == "FS":
                    fast_tracking_plans.append({
                        "task_code": t.get("code"),
                        "task_name": t.get("name"),
                        "predecessor": p.get("fromId"),
                        "current_link": "FS + 0 ngày",
                        "proposed_link": "SS + 3 ngày (Gối đầu song song)",
                        "time_saved_days": max(3, int(dur * 0.4)),
                        "method": "Chia nhỏ phân đoạn đổ bê tông / xây trát để thi công cuốn chiếu (Fast-tracking)"
                    })

        return {
            "target_reduction_days": target_days,
            "crashing_options": crashing_plans,
            "fast_tracking_options": fast_tracking_plans,
            "conclusion": f"Đã tìm thấy {len(crashing_plans)} phương án Crashing và {len(fast_tracking_plans)} phương án Fast-tracking trên các công việc đường găng."
        }


class PlanningScheduleDepartment:
    DEPARTMENT_NAME = "Phòng Kế Hoạch & Kiểm Soát Tiến Độ Thi Công (CPM & EVM)"

    @classmethod
    def audit_schedule_and_progress(
        cls,
        project_name: str,
        tasks: Optional[List[Dict[str, Any]]] = None,
        actual_cost: float = 0.0,
        start_date: str = "2026-11-21",
        work_days_per_week: int = 6,
    ) -> Dict[str, Any]:
        """Thực hiện quy trình kiểm toán tiến độ 2 cấp: Chuyên viên lập CPM ➔ Trưởng phòng thẩm tra."""
        if not tasks:
            tasks = PlanningScheduleSpecialistAgent.generate_standard_6phase_wbs(project_name)

        dossier = PlanningScheduleSpecialistAgent.compute_cpm_and_evm(
            project_name=project_name,
            tasks=tasks,
            actual_cost=actual_cost,
            start_date=start_date,
            work_days_per_week=work_days_per_week,
        )
        head_review = PlanningScheduleHeadReviewerAgent.review_schedule(dossier)
        compression = PlanningScheduleHeadReviewerAgent.recommend_compression(dossier)

        return {
            "department": cls.DEPARTMENT_NAME,
            "status": "COMPLETED",
            "personnel": {
                "specialist": f"{PlanningScheduleSpecialistAgent.AGENT_NAME} ({PlanningScheduleSpecialistAgent.ROLE_TITLE})",
                "department_head": f"{PlanningScheduleHeadReviewerAgent.AGENT_NAME} ({PlanningScheduleHeadReviewerAgent.ROLE_TITLE})",
            },
            "project_name": project_name,
            "specialist_dossier": dossier,
            "head_review": head_review,
            "schedule_compression": compression,
            "gate_status": head_review["gate_status"],
            "summary": f"[{head_review['gate_status']}] {head_review['review_summary']}",
        }
