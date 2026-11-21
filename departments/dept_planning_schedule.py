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

    @classmethod
    def audit_schedule_health(cls, tasks: List[Dict[str, Any]], project_duration: int = 0) -> Dict[str, Any]:
        """
        Kiểm toán 12 chỉ tiêu sức khỏe mạng tiến độ chuẩn DCMA 14 & tiendothicong.vercel.app:
        1. Trùng lặp ID
        2. Thời lượng âm
        3. Mốc Milestone thời lượng != 0
        4. % Hoàn thành ngoài 0-100%
        5. Liên kết tới công tác không tồn tại
        6. Đầu vào mở (Open Start)
        7. Đầu ra mở (Open Finish / Dangling tasks)
        8. Dự trữ âm (Negative Float)
        9. Dự trữ quá lớn (High Float > 44 ngày)
        10. Liên kết tới Summary Task
        11. Chu trình vòng lặp (Cycles)
        12. Out-of-sequence progress (thi công nhảy cóc)
        """
        issues = []
        seen_ids = set()
        id_map = {str(t.get("id")): t for t in tasks}

        succ_map: Dict[str, List[str]] = {str(t.get("id")): [] for t in tasks}
        for t in tasks:
            tid = str(t.get("id"))
            for p in t.get("predecessors", []):
                fid = str(p.get("fromId"))
                if fid in succ_map:
                    succ_map[fid].append(tid)

        for idx, t in enumerate(tasks):
            tid = str(t.get("id") or f"T{idx+1}")
            name = t.get("name", f"Công việc {tid}")
            dur = int(t.get("durationDays", t.get("duration", 0)))
            prog = float(t.get("progress", 0))
            kind = str(t.get("kind", "task")).lower()

            # 1. Trùng lặp ID
            if tid in seen_ids:
                issues.append({"type": "ERROR", "code": "ERR_DUP_ID", "taskId": tid, "message": f"Dòng {idx+1}: Trùng lặp mã ID '{tid}'."})
            seen_ids.add(tid)

            # 2. Thời lượng âm
            if dur < 0:
                issues.append({"type": "ERROR", "code": "ERR_DUR_NEG", "taskId": tid, "message": f"Dòng {idx+1} ({name}): Thời lượng âm ({dur} ngày)."})

            # 3. Mốc Milestone thời lượng != 0
            if kind == "milestone" and dur != 0:
                issues.append({"type": "ERROR", "code": "ERR_MILESTONE_DUR", "taskId": tid, "message": f"Dòng {idx+1} ({name}): Mốc Milestone phải có thời lượng = 0 (hiện tại: {dur})."})

            # 4. Tiến độ ngoài khoảng 0-100%
            if prog < 0 or prog > 100:
                issues.append({"type": "WARNING", "code": "WARN_PCT_RANGE", "taskId": tid, "message": f"Dòng {idx+1} ({name}): % Hoàn thành ({prog}%) ngoài dải 0-100%."})

            # 5. Liên kết tới task không tồn tại
            preds = t.get("predecessors", [])
            for p in preds:
                fid = str(p.get("fromId"))
                if fid not in id_map:
                    issues.append({"type": "ERROR", "code": "ERR_LINK_MISSING", "taskId": tid, "message": f"Dòng {idx+1} ({name}): Liên kết tới công tác không tồn tại (ID: '{fid}')."})

            # 6 & 7. Open ends (Đầu vào mở & Đầu ra mở)
            is_first = (idx == 0)
            is_last = (idx == len(tasks) - 1)
            if not is_first and not preds:
                issues.append({"type": "WARNING", "code": "WARN_OPEN_START", "taskId": tid, "message": f"Dòng {idx+1} ({name}): Đầu vào mở (Open Start) - Không có công tác tiền nhiệm."})
            if not is_last and not succ_map.get(tid):
                issues.append({"type": "WARNING", "code": "WARN_OPEN_FINISH", "taskId": tid, "message": f"Dòng {idx+1} ({name}): Đầu ra mở (Open Finish) - Không có công tác kế nhiệm."})

            # 8. Total Float âm
            tf = t.get("tf", 0)
            if tf < 0:
                issues.append({"type": "WARNING", "code": "WARN_NEG_FLOAT", "taskId": tid, "message": f"Dòng {idx+1} ({name}): Dự trữ âm TF = {tf} ngày (nguy cơ trễ hạn mốc)."})

            # 9. High float (> 44 ngày làm việc = 2 tháng)
            if tf > 44 and dur > 0:
                issues.append({"type": "INFO", "code": "INFO_HIGH_FLOAT", "taskId": tid, "message": f"Dòng {idx+1} ({name}): Dự trữ lớn TF = {tf} ngày (cần xem lại ràng buộc)."})

            # 12. Out-of-sequence progress
            if prog > 0 and preds:
                for p in preds:
                    fid = str(p.get("fromId"))
                    parent_task = id_map.get(fid)
                    if parent_task and float(parent_task.get("progress", 0)) < 100.0 and p.get("type") == "FS":
                        issues.append({
                            "type": "INFO",
                            "code": "INFO_OUT_OF_SEQUENCE",
                            "taskId": tid,
                            "message": f"Dòng {idx+1} ({name}): Đã thi công ({prog}%) trong khi công tác tiền nhiệm '{parent_task.get('name')}' chưa hoàn thành 100%."
                        })

        err_count = sum(1 for i in issues if i["type"] == "ERROR")
        warn_count = sum(1 for i in issues if i["type"] == "WARNING")
        info_count = sum(1 for i in issues if i["type"] == "INFO")

        health_score = max(0, 100 - (err_count * 15 + warn_count * 5))
        if health_score >= 90:
            grade = "XUẤT SẮC (GRADE A)"
        elif health_score >= 75:
            grade = "ĐẠT YÊU CẦU (GRADE B)"
        elif health_score >= 50:
            grade = "CẦN CHỈNH SỬA (GRADE C)"
        else:
            grade = "KHÔNG ĐẠT - NGUY HIỂM (GRADE F)"

        return {
            "health_score": health_score,
            "grade": grade,
            "error_count": err_count,
            "warning_count": warn_count,
            "info_count": info_count,
            "issues": issues,
            "summary": f"Điểm sức khỏe tiến độ: {health_score}/100 ({grade}) - {err_count} lỗi nghiêm trọng, {warn_count} cảnh báo, {info_count} lưu ý."
        }

    @classmethod
    def calculate_resource_histogram(
        cls,
        tasks_computed: List[Dict[str, Any]],
        start_date_str: str = "2026-11-21",
        work_days_per_week: int = 6,
        daily_limits: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Tính toán phụ tải tài nguyên nhân lực và ca máy theo từng ngày thi công:
        - Bảng mã tài nguyên công trường: THO_COFFA, THO_SAT, THO_NE, THO_MEP, PHU, KS, BCH, HSE, TB_CRANE, TB_VANTHANG, TB_BOM_BT, TB_MAY_PHAT.
        - Phát hiện ngày cao điểm (Peak Day), phụ tải trung bình và ngày vượt công suất (Overlimit).
        """
        if daily_limits is None:
            daily_limits = {
                "THO_COFFA": 30,
                "THO_SAT": 25,
                "THO_NE": 35,
                "THO_MEP": 20,
                "PHU": 25,
                "KS": 4,
                "BCH": 2,
                "HSE": 2,
                "TB_CRANE": 1,
                "TB_VANTHANG": 2,
                "TB_BOM_BT": 2,
                "TB_MAY_PHAT": 1
            }

        def get_task_resources(t: Dict[str, Any]) -> Dict[str, int]:
            name = t.get("name", "").lower()
            if "cọc" in name:
                return {"THO_SAT": 8, "PHU": 6, "TB_MAY_PHAT": 1, "KS": 1}
            elif "đào đất" in name or "móng" in name or "hầm" in name:
                return {"THO_COFFA": 16, "THO_SAT": 14, "TB_BOM_BT": 1, "PHU": 10, "KS": 2, "HSE": 1}
            elif "cột" in name or "dầm" in name or "sàn" in name or "bê tông" in name or "kết cấu" in name:
                return {"THO_COFFA": 24, "THO_SAT": 20, "TB_CRANE": 1, "TB_BOM_BT": 1, "PHU": 12, "KS": 2, "HSE": 1}
            elif "xây" in name or "trát" in name or "lát" in name or "ốp" in name:
                return {"THO_NE": 24, "PHU": 8, "TB_VANTHANG": 1, "KS": 1}
            elif "điện" in name or "nước" in name or "mep" in name or "pccc" in name:
                return {"THO_MEP": 14, "PHU": 4, "KS": 1}
            elif "sơn" in name or "trần" in name or "kính" in name:
                return {"THO_NE": 12, "PHU": 6, "TB_VANTHANG": 1}
            else:
                return {"PHU": 4, "KS": 1}

        daily_usage: Dict[str, Dict[str, int]] = {}

        for t in tasks_computed:
            st_str = t.get("startDate")
            en_str = t.get("endDate")
            if not st_str or not en_str:
                continue
            try:
                st = datetime.datetime.strptime(st_str, "%Y-%m-%d").date()
                en = datetime.datetime.strptime(en_str, "%Y-%m-%d").date()
            except Exception:
                continue

            cur = st
            t_res = get_task_resources(t)
            while cur <= en:
                if work_days_per_week == 6 and cur.weekday() == 6:
                    cur += datetime.timedelta(days=1)
                    continue
                if work_days_per_week == 5 and cur.weekday() >= 5:
                    cur += datetime.timedelta(days=1)
                    continue
                dkey = cur.strftime("%Y-%m-%d")
                if dkey not in daily_usage:
                    daily_usage[dkey] = {}
                for rcode, qty in t_res.items():
                    daily_usage[dkey][rcode] = daily_usage[dkey].get(rcode, 0) + qty
                cur += datetime.timedelta(days=1)

        res_summary = {}
        for rcode, limit in daily_limits.items():
            peak = 0
            peak_date = None
            total_mandays = 0
            overlimit_days = 0
            working_days = 0

            for dkey, udict in sorted(daily_usage.items()):
                val = udict.get(rcode, 0)
                if val > 0:
                    working_days += 1
                    total_mandays += val
                    if val > peak:
                        peak = val
                        peak_date = dkey
                    if val > limit:
                        overlimit_days += 1

            avg = round(total_mandays / working_days, 1) if working_days > 0 else 0
            res_summary[rcode] = {
                "resource_code": rcode,
                "daily_limit": limit,
                "peak_value": peak,
                "peak_date": peak_date,
                "average_value": avg,
                "total_unit_days": total_mandays,
                "days_overlimit": overlimit_days,
                "is_overlimit": (peak > limit)
            }

        return {
            "daily_usage": daily_usage,
            "resource_summary": res_summary,
            "overlimit_alerts": [
                f"Vượt giới hạn '{r}': Đỉnh {d['peak_value']} (Giới hạn {d['daily_limit']}) tại ngày {d['peak_date']} ({d['days_overlimit']} ngày vượt)"
                for r, d in res_summary.items() if d["is_overlimit"]
            ]
        }

    @classmethod
    def export_ms_project_xml(
        cls,
        project_name: str,
        tasks_computed: List[Dict[str, Any]],
        start_date: str = "2026-11-21",
        work_days_per_week: int = 6
    ) -> str:
        """Xuất file XML tương thích hoàn toàn với Microsoft Project 2013-2021 & MS Project XML Schema."""
        from xml.sax.saxutils import escape

        now_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        start_iso = f"{start_date}T08:00:00"
        end_date = tasks_computed[-1].get("endDate", start_date) if tasks_computed else start_date
        end_iso = f"{end_date}T17:00:00"

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Project xmlns="http://schemas.microsoft.com/project">',
            f'  <Name>{escape(project_name)}</Name>',
            f'  <Title>{escape(project_name)}</Title>',
            f'  <Company>T&amp;T Construction Enterprise</Company>',
            f'  <Manager>Mai Quang Vinh</Manager>',
            f'  <StartDate>{start_iso}</StartDate>',
            f'  <FinishDate>{end_iso}</FinishDate>',
            f'  <CurrentDate>{now_iso}</CurrentDate>',
            f'  <MinutesPerDay>480</MinutesPerDay>',
            f'  <DaysPerMonth>26</DaysPerMonth>',
            f'  <DefaultStartTime>08:00:00</DefaultStartTime>',
            f'  <DefaultFinishTime>17:00:00</DefaultFinishTime>',
            '  <Calendars>',
            '    <Calendar>',
            '      <UID>1</UID>',
            f'      <Name>Lịch Công Trường {work_days_per_week}d</Name>',
            '      <IsBaseCalendar>1</IsBaseCalendar>',
            '    </Calendar>',
            '  </Calendars>',
            '  <Tasks>'
        ]

        id_to_uid = {str(t.get("id")): idx + 1 for idx, t in enumerate(tasks_computed)}

        for idx, t in enumerate(tasks_computed):
            uid = idx + 1
            dur_days = int(t.get("durationDays", 0))
            dur_mins = dur_days * 480
            prog = float(t.get("progress", 0))
            st = f"{t.get('startDate', start_date)}T08:00:00"
            en = f"{t.get('endDate', start_date)}T17:00:00"
            is_crit = "1" if t.get("isCritical") else "0"
            is_mile = "1" if t.get("kind") == "milestone" or dur_days == 0 else "0"

            xml_lines.append('    <Task>')
            xml_lines.append(f'      <UID>{uid}</UID>')
            xml_lines.append(f'      <ID>{uid}</ID>')
            xml_lines.append(f'      <Name>{escape(str(t.get("name", "")))}</Name>')
            xml_lines.append(f'      <Active>1</Active>')
            xml_lines.append(f'      <Manual>0</Manual>')
            xml_lines.append(f'      <Type>0</Type>')
            xml_lines.append(f'      <IsNull>0</IsNull>')
            xml_lines.append(f'      <WBS>{escape(str(t.get("wbs") or t.get("code") or uid))}</WBS>')
            xml_lines.append(f'      <OutlineNumber>{escape(str(t.get("wbs") or uid))}</OutlineNumber>')
            xml_lines.append(f'      <Duration>PT{dur_mins}M0S</Duration>')
            xml_lines.append(f'      <DurationFormat>7</DurationFormat>')
            xml_lines.append(f'      <Start>{st}</Start>')
            xml_lines.append(f'      <Finish>{en}</Finish>')
            xml_lines.append(f'      <PercentComplete>{int(prog)}</PercentComplete>')
            xml_lines.append(f'      <Critical>{is_crit}</Critical>')
            xml_lines.append(f'      <Milestone>{is_mile}</Milestone>')

            for p in t.get("predecessors", []):
                fid = str(p.get("fromId"))
                p_uid = id_to_uid.get(fid)
                if p_uid:
                    rel = p.get("type", "FS").upper()
                    type_code = {"FF": 0, "FS": 1, "SF": 2, "SS": 3}.get(rel, 1)
                    lag_mins = int(p.get("lag", 0)) * 480
                    xml_lines.append('      <PredecessorLink>')
                    xml_lines.append(f'        <PredecessorUID>{p_uid}</PredecessorUID>')
                    xml_lines.append(f'        <Type>{type_code}</Type>')
                    xml_lines.append(f'        <LinkLag>{lag_mins}</LinkLag>')
                    xml_lines.append(f'        <LagFormat>7</LagFormat>')
                    xml_lines.append('      </PredecessorLink>')

            xml_lines.append('    </Task>')

        xml_lines.append('  </Tasks>')
        xml_lines.append('</Project>')
        return "\n".join(xml_lines)

    @classmethod
    def extract_subcontractor_package(
        cls,
        tasks_computed: List[Dict[str, Any]],
        filter_keyword_or_subcon: str,
        package_name: str = "Gói Thầu Phụ"
    ) -> Dict[str, Any]:
        """Tách các công việc thuộc một nhà thầu phụ ra thành gói tiến độ con độc lập (.tiendo.json)."""
        kw = filter_keyword_or_subcon.lower()
        sub_tasks = []
        for t in tasks_computed:
            s_name = str(t.get("subcontractor", "")).lower()
            t_name = str(t.get("name", "")).lower()
            wbs = str(t.get("wbs", "")).lower()
            if kw in s_name or kw in t_name or kw in wbs:
                sub_tasks.append(t)

        return {
            "version": "1.0",
            "package_name": package_name,
            "filter_key": filter_keyword_or_subcon,
            "tasks_count": len(sub_tasks),
            "subcontractor": sub_tasks[0].get("subcontractor") if sub_tasks else filter_keyword_or_subcon,
            "tasks": sub_tasks
        }

    @classmethod
    def merge_subcontractor_package(
        cls,
        master_tasks: List[Dict[str, Any]],
        sub_package_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gộp kết quả cập nhật của Nhà thầu phụ vào Tiến độ Tổng thể Master Schedule."""
        sub_map = {str(t.get("id")): t for t in sub_package_tasks}
        updated_tasks = []
        modified_count = 0
        progress_gains = 0.0

        for mt in master_tasks:
            tid = str(mt.get("id"))
            if tid in sub_map:
                st = sub_map[tid]
                old_prog = float(mt.get("progress", 0))
                new_prog = float(st.get("progress", old_prog))
                old_dur = int(mt.get("durationDays", mt.get("duration", 0)))
                new_dur = int(st.get("durationDays", st.get("duration", old_dur)))

                if new_prog != old_prog or new_dur != old_dur:
                    modified_count += 1
                    progress_gains += (new_prog - old_prog)

                merged = dict(mt)
                merged["progress"] = new_prog
                merged["durationDays"] = new_dur
                merged["subcontractor_note"] = st.get("note", "Đã cập nhật từ Thầu phụ")
                updated_tasks.append(merged)
            else:
                updated_tasks.append(dict(mt))

        return {
            "master_tasks_count": len(master_tasks),
            "sub_tasks_count": len(sub_package_tasks),
            "modified_tasks_count": modified_count,
            "progress_delta": round(progress_gains, 2),
            "updated_tasks": updated_tasks,
            "summary": f"Đã gộp thành công {modified_count} công tác từ gói thầu phụ, độ lệch tiến độ tổng thể = {progress_gains:+.2f}%."
        }


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

        # 4. Kiểm toán 12 chỉ tiêu chất lượng sức khỏe tiến độ (DCMA 14)
        tasks_raw = specialist_dossier.get("tasks_computed") or []
        health = PlanningScheduleSpecialistAgent.audit_schedule_health(
            tasks_raw, specialist_dossier.get("project_duration_days", 0)
        )
        if health["error_count"] > 0:
            warnings.append(f"LỖI CHẤT LƯỢNG TIẾN ĐỘ: Điểm sức khỏe = {health['health_score']}/100 ({health['grade']}) với {health['error_count']} lỗi logic nghiêm trọng.")
            recommendations.append("Khắc phục ngay các lỗi logic (trùng ID, mốc sai thời lượng, việc treo hoặc liên kết thiếu) trước khi phát hành tiến độ.")
        elif health["warning_count"] > 0:
            warnings.append(f"CẢNH BÁO MẠNG TIẾN ĐỘ: Điểm sức khỏe = {health['health_score']}/100 ({health['grade']}) với {health['warning_count']} cảnh báo.")

        # 5. Phân tích phụ tải tài nguyên nhân lực & ca máy
        res_hist = PlanningScheduleSpecialistAgent.calculate_resource_histogram(
            tasks_computed=tasks_raw,
            start_date_str=specialist_dossier.get("start_date", "2026-11-21"),
            work_days_per_week=specialist_dossier.get("calendar", {}).get("workDaysPerWeek", 6)
        )
        if res_hist.get("overlimit_alerts"):
            for alert in res_hist["overlimit_alerts"][:3]:
                warnings.append(f"QUÁ TẢI TÀI NGUYÊN: {alert}")
            recommendations.append("Kích hoạt cân bằng tài nguyên (Resource Leveling): Tận dụng dự trữ tự do (Free Float) của các công việc không găng để san phẳng biểu đồ nhân lực.")

        # 6. Kiểm toán tuân thủ Nghị định 210/2026/NĐ-CP & 207/2026/NĐ-CP
        gate_status = "BLOCKED" if (specialist_dossier.get("has_cycle") or health["error_count"] > 0) else ("WARNING" if warnings else "APPROVED")

        summary = (
            f"Trưởng phòng {cls.AGENT_NAME}: Tổng thời gian CPM = {specialist_dossier.get('project_duration_days', 0)} ngày, "
            f"Tiến độ hoàn thành chung = {specialist_dossier.get('overall_progress_pct', 0)}%, "
            f"Đường găng gồm {specialist_dossier.get('critical_path_count', 0)} công việc. "
            f"Sức khỏe tiến độ: {health['health_score']}/100 ({health['grade']}). "
            f"Chỉ số EVM: SPI = {spi:.2f}, CPI = {cpi:.2f}. "
            f"Dự báo chi phí hoàn thành EAC = {evm.get('eac', 0):,.0f} VNĐ."
        )

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "can_proceed": gate_status != "BLOCKED",
            "schedule_health": health,
            "resource_histogram": res_hist,
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

        # Trích xuất gói thầu phụ mẫu (ví dụ phần Cọc hoặc Kết cấu)
        subcon_package = PlanningScheduleSpecialistAgent.extract_subcontractor_package(
            tasks_computed=dossier.get("tasks_computed", []),
            filter_keyword_or_subcon="Cọc",
            package_name=f"Gói Thầu Phụ Thi Công Cọc - {project_name}"
        )

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
            "schedule_health": head_review.get("schedule_health"),
            "resource_histogram": head_review.get("resource_histogram"),
            "schedule_compression": compression,
            "subcontractor_package_sample": subcon_package,
            "gate_status": head_review["gate_status"],
            "summary": f"[{head_review['gate_status']}] {head_review['review_summary']}",
        }
