# -*- coding: utf-8 -*-
"""
GITHUB SYNC AUTOMATION MODULE:
Tự động đồng bộ hóa mã nguồn giữa Antigravity IDE và GitHub cá nhân của Founder:
https://github.com/MaiVinh1302/one-person-ai-construction-firm
"""

import subprocess
import os
from typing import Dict, Any

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class GitHubAutoSync:
    GITHUB_REPO_URL = "https://github.com/MaiVinh1302/one-person-ai-construction-firm"

    @classmethod
    def get_sync_status(cls) -> Dict[str, Any]:
        """Kiểm tra tình trạng đồng bộ giữa local và remote"""
        try:
            status_out = subprocess.run(
                ["git", "status", "-s"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            branch_out = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            last_commit = subprocess.run(
                ["git", "log", "-1", "--format=%h - %s (%cd)", "--date=format:%d/%m/%Y %H:%M"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )

            has_uncommitted = bool(status_out.stdout.strip())

            return {
                "repo_url": cls.GITHUB_REPO_URL,
                "branch": branch_out.stdout.strip() or "main",
                "has_uncommitted_changes": has_uncommitted,
                "uncommitted_files": status_out.stdout.strip().split("\n") if has_uncommitted else [],
                "latest_commit": last_commit.stdout.strip(),
                "status": "CHỜ ĐỒNG BỘ" if has_uncommitted else "ĐÃ ĐỒNG BỘ 100%"
            }
        except Exception as e:
            return {
                "error": str(e),
                "repo_url": cls.GITHUB_REPO_URL,
                "status": "LỖI KIỂM TRA"
            }

    @classmethod
    def commit_and_push(cls, commit_message: str = "auto: update codebase from Antigravity AI") -> Dict[str, Any]:
        """Tự động stage, commit và push lên GitHub"""
        try:
            # 1. git add .
            subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)

            # 2. git status check
            status_res = subprocess.run(["git", "status", "-s"], cwd=REPO_DIR, capture_output=True, text=True)
            if not status_res.stdout.strip():
                return {
                    "success": True,
                    "message": "Mã nguồn đã đồng bộ hoàn toàn với GitHub, không có thay đổi mới cần đẩy.",
                    "repo_url": cls.GITHUB_REPO_URL
                }

            # 3. git commit
            subprocess.run(["git", "commit", "-m", commit_message], cwd=REPO_DIR, check=True)

            # 4. git push
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)
            if push_res.returncode == 0:
                return {
                    "success": True,
                    "message": f"Đã tự động đẩy thành công các cập nhật lên GitHub: {commit_message}",
                    "repo_url": cls.GITHUB_REPO_URL
                }
            else:
                return {
                    "success": False,
                    "error": push_res.stderr or push_res.stdout,
                    "message": "Không thể đẩy trực tiếp lên GitHub từ sandbox không có mạng."
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
