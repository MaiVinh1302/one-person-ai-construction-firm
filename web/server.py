# -*- coding: utf-8 -*-
"""
WEB SERVER & DASHBOARD: One-Person AI Construction Firm Portal
FastAPI backend phục vụ giao diện điều hành Web & Mobile PWA cho Founder Mai Quang Vinh.
Hỗ trợ:
- Quản lý 5 phòng ban ảo với cơ cấu 2 cấp nhân sự (Chuyên viên + Trưởng phòng)
- Hệ thống báo cáo toàn diện: Báo cáo Tổng thể Công ty, Báo cáo Riêng từng Phòng ban, Báo cáo Tổng hợp Chuyên đề
- Tải về file Word .docx chuẩn Nghị định 30/2020/NĐ-CP
"""

import os
import sys
import base64
import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

from core.orchestrator import orchestrator
from core.permissions import RBACManager
from core.reporting_engine import reporting_engine, REPORTS_DIR
from core.github_sync import GitHubAutoSync
from knowledge.legal_engine import legal_engine
from knowledge.corporate_sops import corporate_sop_engine

app = FastAPI(title="One-Person AI Construction Firm Portal", version="1.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api/status")
def get_system_status():
    return {
        "company_name": "T&T AI Construction Consulting & Management",
        "founder": orchestrator.founder_name,
        "operating_mode": "1-Person AI Solopreneur Enterprise",
        "legal_library_status": "CONNECTED" if legal_engine.has_excel else "STANDBY",
        "legal_library_path": legal_engine.legal_dir,
        "cached_laws_count": len(legal_engine.cached_laws),
        "roster": orchestrator.get_firm_roster(),
        "departments_count": len(orchestrator.get_firm_roster()),
        "pending_approvals_count": len([a for a in orchestrator.pending_approvals if "CHỜ" in a["status"]]),
        "gate_transfers_count": len(orchestrator.gate_transfer_log),
        "reports_count": len(orchestrator.generated_reports)
    }

@app.get("/api/roster")
def get_roster():
    """Trả về danh bạ cơ cấu tổ chức 2 cấp nhân sự cho toàn bộ 5 phòng ban"""
    return {
        "founder": orchestrator.founder_name,
        "roster": orchestrator.get_firm_roster()
    }

@app.get("/api/permissions")
def get_permissions():
    return {"matrix": RBACManager.get_approval_matrix()}

@app.post("/api/audit")
async def run_audit(request: Request):
    body = await request.json()
    wf_type = body.get("workflow", "CONTRACT")
    payload = body.get("payload", {})
    res = orchestrator.dispatch_audit(wf_type, payload)
    return res

@app.get("/api/tasks")
def get_assigned_tasks():
    """Trả về danh sách các nhiệm vụ Founder đã giao cho các phòng ban AI"""
    return {"tasks": orchestrator.assigned_tasks}

@app.post("/api/tasks")
async def create_assigned_task(request: Request):
    """Giao việc mới từ Founder cho 1 hoặc nhiều phòng ban"""
    body = await request.json()
    res = orchestrator.assign_task(
        task_title=body.get("task_title", "Thẩm tra hồ sơ dự án trọng điểm"),
        project_name=body.get("project_name", "Dự án Tổ hợp T&T Tower"),
        assigned_workflows=body.get("assigned_workflows", ["CONTRACT"]),
        priority=body.get("priority", "URGENT"),
        deadline=body.get("deadline", "2026-11-15"),
        founder_instruction=body.get("founder_instruction", ""),
        custom_payloads=body.get("custom_payloads")
    )
    return res

# -------------------------------------------------------------
# REPORTING API ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/reports")
def get_reports_list():
    """Trả về danh sách tất cả các báo cáo đã sinh trong phiên làm việc"""
    return {"reports": orchestrator.generated_reports}

@app.post("/api/reports/master")
async def generate_master_report(request: Request):
    """Sinh Bản Báo Cáo Tổng Thể Công Ty (Master Executive Dossier)"""
    body = await request.json() if await request.body() else {}
    proj_name = body.get("project_name", "Tổ hợp Thương mại & Văn phòng T&T Tower")
    proj_code = body.get("project_code", "DA-TT-2026-HQ")
    report = orchestrator.generate_master_company_report(
        project_name=proj_name,
        project_code=proj_code,
        custom_payloads=body.get("custom_payloads")
    )
    return report

@app.post("/api/reports/modular")
async def generate_modular_report(request: Request):
    """Sinh Báo Cáo Tổng Hợp Chuyên Đề Theo Yêu Cầu (Chỉ gom các phòng ban được chọn)"""
    body = await request.json()
    selected_wfs = body.get("workflows", ["CONTRACT", "BIDDING"])
    theme = body.get("theme", "Báo Cáo Tổng Hợp Chuyên Đề Nghiệp Vụ Xây Dựng")
    proj_name = body.get("project_name", "Dự án Tổ hợp T&T Tower")
    report = orchestrator.generate_modular_report(
        selected_workflows=selected_wfs,
        custom_payloads=body.get("custom_payloads"),
        report_theme=theme,
        project_name=proj_name
    )
    return report

@app.get("/api/reports/download/{filename}")
def download_report_file(filename: str):
    """Tải file báo cáo Word .docx về máy tính của Founder"""
    file_path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp báo cáo.")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# -------------------------------------------------------------
# FILE UPLOAD & DOSSIER ATTACHMENT ENDPOINTS
# -------------------------------------------------------------
@app.post("/api/upload")
async def upload_department_file(request: Request):
    """Tải lên hồ sơ giao việc cho từng phòng ban (lưu vào thư mục uploads/)"""
    body = await request.json()
    raw_name = body.get("filename", "ho_so_giao_viec.pdf")
    safe_name = os.path.basename(raw_name)
    dept = body.get("department", "GENERAL")
    content_b64 = body.get("content_base64", "")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_filename = f"{dept}_{timestamp}_{safe_name}"
    saved_path = os.path.join(UPLOADS_DIR, saved_filename)

    if content_b64:
        try:
            if "," in content_b64:
                content_b64 = content_b64.split(",", 1)[1]
            file_bytes = base64.b64decode(content_b64)
            with open(saved_path, "wb") as f:
                f.write(file_bytes)
        except Exception:
            with open(saved_path, "w", encoding="utf-8") as f:
                f.write(f"Uploaded file metadata: {safe_name}")
    else:
        with open(saved_path, "w", encoding="utf-8") as f:
            f.write(f"Uploaded file metadata: {safe_name}")

    return {
        "success": True,
        "original_name": safe_name,
        "saved_filename": saved_filename,
        "download_url": f"/api/uploads/download/{saved_filename}"
    }

@app.get("/api/uploads/download/{filename}")
def download_uploaded_file(filename: str):
    """Tải xuống hoặc xem lại hồ sơ đã giao việc cho phòng ban"""
    safe_name = os.path.basename(filename)
    file_path = os.path.join(UPLOADS_DIR, safe_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp hồ sơ đính kèm.")
    return FileResponse(path=file_path, filename=safe_name)

# -------------------------------------------------------------
# GITHUB AUTO-SYNC ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/github/status")
def get_github_sync_status():
    """Lấy trạng thái đồng bộ với repository GitHub"""
    return GitHubAutoSync.get_sync_status()

@app.post("/api/github/sync")
async def sync_github_now(request: Request):
    """Kích hoạt đồng bộ hóa tức thời lên GitHub"""
    body = await request.json() if await request.body() else {}
    msg = body.get("message", "auto: sync updates from Antigravity Dashboard")
    return GitHubAutoSync.commit_and_push(msg)

@app.get("/api/approvals")
def get_approvals():
    return {"approvals": orchestrator.pending_approvals}

@app.post("/api/approvals/{approval_id}/action")
async def act_on_approval(approval_id: str, request: Request):
    body = await request.json()
    action = body.get("action", "APPROVE")
    note = body.get("note", "")
    res = orchestrator.founder_action(approval_id, action, note)
    return res

@app.get("/api/legal/search")
def search_legal_library(keyword: str = "", domain: str = None):
    results = legal_engine.search_law(keyword, domain)
    return {"query": keyword, "count": len(results), "results": results[:20]}

@app.get("/api/sops")
def get_corporate_sops():
    """Trả về toàn bộ Hệ thống Quy trình, Quy chế & Biểu mẫu nội bộ Tập đoàn T&T đã chắt lọc"""
    return corporate_sop_engine.get_all_pillars_summary()

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    html_file = os.path.join(static_dir, "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>One-Person AI Construction Firm Portal</h1>"

if __name__ == "__main__":
    uvicorn.run("web.server:app", host="0.0.0.0", port=8000, reload=True)
