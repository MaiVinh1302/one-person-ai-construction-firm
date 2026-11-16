# -*- coding: utf-8 -*-
"""
DEPARTMENT 7: Planning, CPM Scheduling & Progress Reporting
(Phòng Kế hoạch & Kiểm soát Tiến độ Thi công)
Cơ cấu 2 cấp nhân sự:
1. Chuyên viên Lập Tiến độ CPM: Trần Tiến Độ (Level 2 Specialist)
   - Lập cây WBS, tính toán đường găng CPM (Forward/Backward Pass, Total Float), cân bằng tài nguyên & tạo dữ liệu S-Curve.
2. Trưởng phòng Kiểm soát Tiến độ & EVM: Nguyễn Kế Hoạch (Level 1 Department Head)
   - Kiểm toán logic mạng găng (phát hiện vòng lặp, công việc treo), phân tích chỉ số EVM (SPI/CPI),
     đối chiếu điều khoản phạt/gia hạn tiến độ theo NĐ 210/2026/NĐ-CP, Nhật ký điện tử theo NĐ 207/2026/NĐ-CP
     và Mẫu 03.a/TT theo NĐ 254/2025/NĐ-CP.
"""

from typing import Dict, List, Any
from core.permissions import RoleLevel


class PlanningScheduleSpecialistAgent:
    AGENT_NAME = "Trần Tiến Độ"
    ROLE_TITLE = "Kỹ sư Lập Tiến độ CPM, WBS & Cân bằng Tài nguyên"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def compute_cpm_and_evm(
        cls,
        project_name: str,
        tasks: List[Dict[str, Any]],
        actual_cost: float = 0.0,
    ) -> Dict[str, Any]:
        """Thực hiện tính toán Forward/Backward Pass CPM & chỉ số EVM."""
        task_map: Dict[str, Dict[str, Any]] = {}
        for idx, t in enumerate(tasks):
            tid = str(t.get("id") or f"T{idx + 1}")
            dur = max(0, int(t.get("durationDays", 1)))
            prog = max(0.0, min(100.0, float(t.get("progress", 0))))
            budget = max(0.0, float(t.get("budget", 0)))
            preds = t.get("predecessors") or []
            task_map[tid] = {
                "id": tid,
                "code": t.get("code") or tid,
                "name": t.get("name") or f"Công việc {tid}",
                "kind": t.get("kind") or "task",
                "durationDays": dur,
                "progress": prog,
                "budget": budget,
                "predecessors": preds,
                "es": 0,
                "ef": dur,
                "ls": 0,
                "lf": dur,
                "tf": 0,
                "isCritical": False,
            }

        # Topo / iterative Forward Pass (với kiểm tra chu trình)
        ids = list(task_map.keys())
        has_cycle = False
        for _ in range(len(ids) + 2):
            changed = False
            for tid in ids:
                cur = task_map[tid]
                es = 0
                for link in cur["predecessors"]:
                    if isinstance(link, str):
                        pid, ltype, lag = link, "FS", 0
                    else:
                        pid = str(link.get("fromId", ""))
                        ltype = str(link.get("type", "FS")).upper()
                        lag = int(link.get("lag", 0))
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

        # Backward Pass
        succ_map: Dict[str, List[Dict[str, Any]]] = {tid: [] for tid in ids}
        for tid in ids:
            for link in task_map[tid]["predecessors"]:
                pid = link if isinstance(link, str) else str(link.get("fromId", ""))
                ltype = "FS" if isinstance(link, str) else str(link.get("type", "FS")).upper()
                lag = 0 if isinstance(link, str) else int(link.get("lag", 0))
                if pid in succ_map:
                    succ_map[pid].append({"toId": tid, "type": ltype, "lag": lag})

        for tid in ids:
            task_map[tid]["lf"] = project_duration
            task_map[tid]["ls"] = project_duration - task_map[tid]["durationDays"]

        for _ in range(len(ids) + 2):
            changed = False
            for tid in reversed(ids):
                cur = task_map[tid]
                lf = project_duration
                for sl in succ_map[tid]:
                    s = task_map[sl["toId"]]
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

        critical_tasks = []
        dangling_tasks = []
        total_budget = 0.0
        earned_value = 0.0
        weighted_progress_sum = 0.0
        total_weight = 0.0

        for tid in ids:
            t = task_map[tid]
            t["tf"] = t["ls"] - t["es"]
            t["isCritical"] = (t["tf"] <= 0 and t["durationDays"] > 0)
            if t["isCritical"]:
                critical_tasks.append(f"{t['code']} - {t['name']} ({t['durationDays']}d)")
            if not succ_map[tid] and t["ef"] < project_duration:
                dangling_tasks.append(f"{t['code']} - {t['name']}")

            w = t["budget"] if t["budget"] > 0 else max(1.0, float(t["durationDays"]))
            total_budget += t["budget"]
            earned_value += t["budget"] * (t["progress"] / 100.0)
            weighted_progress_sum += w * t["progress"]
            total_weight += w

        overall_progress = round(weighted_progress_sum / total_weight, 2) if total_weight > 0 else 0.0
        planned_value = round(total_budget * 0.5, 2) if total_budget > 0 else 0.0
        spi = round(earned_value / planned_value, 3) if planned_value > 0 else 1.0
        cpi = round(earned_value / actual_cost, 3) if actual_cost > 0 else 1.0

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "project_name": project_name,
            "project_duration_days": project_duration,
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
                "spi": spi,
                "cpi": cpi,
            },
            "tasks_computed": list(task_map.values()),
        }


class PlanningScheduleHeadReviewerAgent:
    AGENT_NAME = "Nguyễn Kế Hoạch"
    ROLE_TITLE = "Trưởng phòng Kiểm soát Tiến độ, EVM & Báo cáo Chủ đầu tư"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    @classmethod
    def review_schedule(cls, specialist_dossier: Dict[str, Any]) -> Dict[str, Any]:
        warnings = []
        if specialist_dossier.get("has_cycle"):
            warnings.append("LỖI NGHIÊM TRỌNG: Phát hiện vòng lặp logic tiền nhiệm (Cycle) trong mạng CPM.")
        if specialist_dossier.get("dangling_tasks"):
            warnings.append(
                f"Cảnh báo {len(specialist_dossier['dangling_tasks'])} công việc treo (Dangling Tasks) chưa nối kế nhiệm."
            )
        spi = specialist_dossier.get("evm", {}).get("spi", 1.0)
        if spi < 0.9:
            warnings.append(
                f"SPI = {spi} (< 0.90): Nguy cơ chậm tiến độ hợp đồng! Đề xuất kích hoạt nén tiến độ (Fast-track/Crashing) và lập thông báo theo Nghị định 210/2026/NĐ-CP."
            )

        gate_status = "BLOCKED" if specialist_dossier.get("has_cycle") else ("WARNING" if warnings else "APPROVED")
        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "applicable_law": (
                "Nghị định 210/2026/NĐ-CP (Hợp đồng & Tiến độ), "
                "Nghị định 207/2026/NĐ-CP (Nhật ký thi công điện tử & BBNTCV), "
                "Nghị định 254/2025/NĐ-CP (Mẫu 03.a/TT thanh toán khối lượng)"
            ),
            "can_proceed": gate_status != "BLOCKED",
            "warnings_count": len(warnings),
            "warnings": warnings,
            "review_summary": (
                f"Trưởng phòng {cls.AGENT_NAME}: Tổng thời gian CPM = {specialist_dossier.get('project_duration_days', 0)} ngày, "
                f"Tiến độ chung = {specialist_dossier.get('overall_progress_pct', 0)}%, "
                f"Đường găng = {specialist_dossier.get('critical_path_count', 0)} công việc, SPI = {spi}."
            ),
        }


class PlanningScheduleDepartment:
    DEPARTMENT_NAME = "Phòng Kế hoạch & Kiểm soát Tiến độ Thi công (CPM & EVM)"

    @classmethod
    def audit_schedule_and_progress(
        cls,
        project_name: str,
        tasks: List[Dict[str, Any]],
        actual_cost: float = 0.0,
    ) -> Dict[str, Any]:
        dossier = PlanningScheduleSpecialistAgent.compute_cpm_and_evm(
            project_name=project_name,
            tasks=tasks,
            actual_cost=actual_cost,
        )
        head_review = PlanningScheduleHeadReviewerAgent.review_schedule(dossier)
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
            "gate_status": head_review["gate_status"],
            "summary": f"[{head_review['gate_status']}] {head_review['review_summary']}",
        }
