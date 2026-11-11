# -*- coding: utf-8 -*-
"""
GOOGLE DRIVE CONNECTOR & AUTOMATED DOCUMENT REPOSITORY
Tự động liên kết Google Drive (quangvinh1302@gmail.com):
- Tạo và quản lý kho lưu trữ hồ sơ chuẩn hóa theo từng Dự án (Dự án 1, Dự án 2...)
- Phân chia khu vực khoa học theo 5 Phòng Ban & 10 Cá nhân (Chuyên viên + Trưởng phòng)
- Tự động đồng bộ, tải lên (upload) và cấp quyền truy cập tài liệu, báo cáo Word .docx
"""

import os
import sys
import json
import re
import subprocess
from typing import Dict, List, Any, Optional

GDRIVE_CLI = "gdrive"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gdrive_structure.json")

# Template cây thư mục khoa học chuẩn hóa cho từng dự án xây dựng
PROJECT_FOLDER_TEMPLATE = {
    "01_BAN_PHAP_CHE_HOP_DONG": {
        "code": "CONTRACT",
        "name": "Phòng Pháp chế & Đàm phán Hợp đồng",
        "staff": {
            "01_Chuyen_vien_Nguyen_Van_Phap": {
                "role": "Chuyên viên Soạn thảo & Rà soát Hợp đồng",
                "subfolders": ["Ho_So_Giao_Viec_Dau_Vao", "Du_Thao_Dieu_Khoan_Va_Phu_Luc"]
            },
            "02_Truong_phong_Tran_Thi_Tuan_Thu": {
                "role": "Trưởng phòng Pháp chế & Quản trị Rủi ro",
                "subfolders": ["Bao_Cao_Tham_Tra_Phap_Ly_ND210", "Hop_Dong_Mau_QD690_QD560_Da_Duyet"]
            }
        }
    },
    "02_BAN_DAU_THAU_MUA_SAM": {
        "code": "BIDDING",
        "name": "Phòng Quản lý Đấu thầu & Mua sắm",
        "staff": {
            "01_Chuyen_vien_Le_Quang_Thau": {
                "role": "Chuyên viên Thẩm tra Hồ sơ Đấu thầu & Giá Mua sắm",
                "subfolders": ["Ho_So_Moi_Thau_HSMT_QD458", "Bao_Gia_Va_Ho_So_Du_Thau"]
            },
            "02_Truong_phong_Pham_Minh_Dau": {
                "role": "Trưởng phòng Quản lý Đấu thầu & Hợp đồng Mua sắm",
                "subfolders": ["Bien_Ban_Dam_Phan_BM07", "To_Trinh_Phe_Duyet_KQLCNT_BM08"]
            }
        }
    },
    "03_BAN_KY_SU_DU_TOAN_QS": {
        "code": "QS_BOQ",
        "name": "Phòng Kỹ sư Dự toán QS & BOQ",
        "staff": {
            "01_Chuyen_vien_Do_Van_Luong": {
                "role": "Kỹ sư QS Bóc tách Khối lượng & Áp Định mức",
                "subfolders": ["Ban_Ve_CAD_DXF", "Bang_Tinh_Khoi_Luong_8_Bill_HSMT"]
            },
            "02_Truong_phong_Vu_Dinh_Toan": {
                "role": "Trưởng phòng Thẩm tra Dự toán & Kiểm soát Chi phí",
                "subfolders": ["Ho_So_Phat_Sinh_12_Buoc_QT01", "Bao_Cao_Tham_Tra_BOQ_TT09"]
            }
        }
    },
    "04_BAN_QUAN_LY_CHAT_LUONG_QAQC": {
        "code": "QAQC",
        "name": "Phòng Quản lý Chất lượng QA/QC",
        "staff": {
            "01_Chuyen_vien_Bui_Van_Nghiem": {
                "role": "Kỹ sư QA/QC Giám sát Hiện trường & Hồ sơ Nghiệm thu",
                "subfolders": ["Ket_Qua_Thi_Nghiem_LAS_XD", "Chung_Chi_CO_CQ_Vat_Tu", "Nhat_Ky_Thi_Cong_15BM"]
            },
            "02_Truong_phong_Hoang_Van_Chuan": {
                "role": "Trưởng phòng Quản lý Chất lượng & An toàn Công trình",
                "subfolders": ["Bien_Ban_Nghiem_Thu_BBNTCV_10BM", "Ban_Ve_Hoan_Cong_4_Chu_Ky_ND06"]
            }
        }
    },
    "05_BAN_KIEM_TOAN_THANH_QUYET_TOAN": {
        "code": "SETTLEMENT",
        "name": "Phòng Kiểm toán Thanh & Quyết toán",
        "staff": {
            "01_Chuyen_vien_Ngo_Thi_Quyet": {
                "role": "Chuyên viên Thẩm tra Hồ sơ Thanh Quyết toán Mẫu 08a",
                "subfolders": ["Ho_So_De_Nghi_Thanh_Toan", "Bang_Chi_Tinh_Mau_08a_08b"]
            },
            "02_Truong_phong_Dang_Duc_Toan": {
                "role": "Trưởng phòng Kiểm toán Quyết toán & Kiểm soát Ngân quỹ",
                "subfolders": ["Bao_Cao_Tham_Dinh_KTXD_BM07_BM14", "To_Trinh_CTDH_BM16_Trinh_Founder"]
            }
        }
    },
    "06_HO_SO_TONG_THE_FOUNDER_DUYET": {
        "code": "MASTER_EXECUTIVE",
        "name": "Hồ sơ Tổng thể & Quyết nghị Founder",
        "staff": {
            "Founder_CEO_Mai_Quang_Vinh": {
                "role": "Chủ tịch / Founder điều hành (Level 5)",
                "subfolders": ["Master_Executive_Dossiers_Word", "Quyet_Dinh_Phe_Duyet_Giai_Ngan_Trao_Thau"]
            }
        }
    }
}


class GoogleDriveConnector:
    """
    Trình quản lý & điều phối kho hồ sơ Google Drive cho Doanh nghiệp AI Xây dựng
    """

    def __init__(self):
        self.root_folder_name = "KHO_LUU_TRU_HO_SO_DOANH_NGHIEP_AI_XAY_DUNG"
        self.root_folder_id = "1ZQIUSN-tsDB9j0hGe6YfTw0SG9vMQK-D"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "root_folder_id": self.root_folder_id,
            "root_folder_name": self.root_folder_name,
            "projects": {}
        }

    def _save_cache(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Warning] Khong the luu cache Drive: {e}", file=sys.stderr)

    def _run_gdrive_command(self, args: List[str]) -> Dict[str, Any]:
        """Thực thi lệnh gdrive CLI qua subprocess"""
        cmd = [GDRIVE_CLI] + args
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                shell=True
            )
            stdout = res.stdout.strip()
            stderr = res.stderr.strip()
            success = (res.returncode == 0)
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": res.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Tạo một thư mục trên Google Drive và trả về Folder ID"""
        args = ["mutate", "mkdir", folder_name]
        if parent_id:
            args.extend(["--parent", parent_id])

        res = self._run_gdrive_command(args)
        if res["success"]:
            # Output format: Created folder: Name (ID: XXXXX)
            match = re.search(r"\(ID:\s*([^\)]+)\)", res["stdout"])
            if match:
                folder_id = match.group(1).strip()
                return folder_id
        print(f"[Error] Khong the tao thu muc '{folder_name}': {res['stderr'] or res['stdout']}", file=sys.stderr)
        return None

    def upload_file(self, local_file_path: str, parent_folder_id: Optional[str] = None) -> Dict[str, Any]:
        """Tải một tệp tin từ máy tính lên thư mục chỉ định trên Google Drive"""
        if not os.path.exists(local_file_path):
            return {"success": False, "message": f"Không tìm thấy file: {local_file_path}"}

        args = ["mutate", "upload", local_file_path]
        if parent_folder_id:
            args.extend(["--parent", parent_folder_id])

        res = self._run_gdrive_command(args)
        if res["success"]:
            match = re.search(r"\(ID:\s*([^\)]+)\)", res["stdout"])
            file_id = match.group(1).strip() if match else ""
            file_name = os.path.basename(local_file_path)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view" if file_id else ""
            return {
                "success": True,
                "file_name": file_name,
                "file_id": file_id,
                "drive_url": drive_url,
                "raw_output": res["stdout"]
            }
        return {"success": False, "message": res["stderr"] or res["stdout"]}

    def ensure_root_folder(self) -> str:
        """Đảm bảo thư mục gốc của doanh nghiệp AI tồn tại trên Drive"""
        if self.cache.get("root_folder_id"):
            return self.cache["root_folder_id"]

        folder_id = self.create_folder(self.root_folder_name)
        if folder_id:
            self.cache["root_folder_id"] = folder_id
            self._save_cache()
            return folder_id
        return ""

    def setup_project_repository(self, project_key: str = "DU_AN_1", project_display_name: str = "Dự án 1: Tổ hợp Thương mại & Văn phòng T&T Tower") -> Dict[str, Any]:
        """
        Khởi tạo toàn bộ cây thư mục chuẩn hóa khoa học cho một dự án cụ thể:
        - 5 Phòng Ban (Pháp chế, Đấu thầu, QS, QA/QC, Quyết toán)
        - 10 Nhân sự (Chuyên viên + Trưởng phòng)
        - Hồ sơ Master Executive của Founder
        """
        root_id = self.ensure_root_folder()
        if not root_id:
            return {"success": False, "message": "Không thể kết nối thư mục gốc Google Drive."}

        projects = self.cache.get("projects", {})
        if project_key in projects and projects[project_key].get("folder_id"):
            return {
                "success": True,
                "message": f"Dự án '{project_display_name}' đã được khởi tạo cấu trúc trước đó.",
                "project_data": projects[project_key]
            }

        # 1. Tạo thư mục cấp 1: Tên Dự án
        proj_folder_name = f"📁 {project_key.upper()} - {project_display_name}"
        proj_folder_id = self.create_folder(proj_folder_name, parent_id=root_id)
        if not proj_folder_id:
            return {"success": False, "message": f"Không thể tạo thư mục cho dự án: {project_key}"}

        proj_structure = {
            "project_key": project_key,
            "project_display_name": project_display_name,
            "folder_name": proj_folder_name,
            "folder_id": proj_folder_id,
            "drive_url": f"https://drive.google.com/drive/folders/{proj_folder_id}",
            "departments": {}
        }

        # 2. Tạo các thư mục Phòng ban & Nhân sự
        for dept_dir, dept_info in PROJECT_FOLDER_TEMPLATE.items():
            dept_folder_name = f"🏛️ {dept_dir} - {dept_info['name']}"
            dept_id = self.create_folder(dept_folder_name, parent_id=proj_folder_id)
            if not dept_id:
                continue

            dept_data = {
                "dept_code": dept_info["code"],
                "dept_name": dept_info["name"],
                "folder_name": dept_folder_name,
                "folder_id": dept_id,
                "drive_url": f"https://drive.google.com/drive/folders/{dept_id}",
                "staff": {}
            }

            # 3. Tạo thư mục cho từng nhân sự (Chuyên viên & Trưởng phòng)
            for staff_name, staff_info in dept_info.get("staff", {}).items():
                staff_folder_name = f"👤 {staff_name} ({staff_info['role']})"
                staff_id = self.create_folder(staff_folder_name, parent_id=dept_id)
                if not staff_id:
                    continue

                staff_data = {
                    "staff_name": staff_name,
                    "role": staff_info["role"],
                    "folder_id": staff_id,
                    "drive_url": f"https://drive.google.com/drive/folders/{staff_id}",
                    "subfolders": {}
                }

                # 4. Tạo các thư mục con chức năng chuyên môn
                for sub in staff_info.get("subfolders", []):
                    sub_name = f"📁 {sub}"
                    sub_id = self.create_folder(sub_name, parent_id=staff_id)
                    if sub_id:
                        staff_data["subfolders"][sub] = {
                            "folder_name": sub_name,
                            "folder_id": sub_id,
                            "drive_url": f"https://drive.google.com/drive/folders/{sub_id}"
                        }

                dept_data["staff"][staff_name] = staff_data

            proj_structure["departments"][dept_info["code"]] = dept_data

        projects[project_key] = proj_structure
        self.cache["projects"] = projects
        self._save_cache()

        return {
            "success": True,
            "message": f"Khởi tạo thành công kho lưu trữ chuẩn hóa cho '{project_display_name}'!",
            "project_data": proj_structure
        }

    def setup_default_projects(self) -> Dict[str, Any]:
        """Tự động khởi tạo cả DỰ ÁN 1 và DỰ ÁN 2 trên Google Drive"""
        res1 = self.setup_project_repository("DU_AN_1", "Dự án 1 (Tổ hợp Thương mại & Văn phòng T&T Tower)")
        res2 = self.setup_project_repository("DU_AN_2", "Dự án 2 (Khu Đô thị Sinh thái Nghỉ dưỡng T&T Eco City)")
        return {
            "root_folder_id": self.root_folder_id,
            "root_url": f"https://drive.google.com/drive/folders/{self.root_folder_id}",
            "du_an_1": res1,
            "du_an_2": res2
        }

    def upload_department_report(
        self,
        project_key: str,
        dept_code: str,
        is_head: bool,
        file_path: str,
        category: str = "Bao_Cao"
    ) -> Dict[str, Any]:
        """Tải một báo cáo hoặc hồ sơ lên đúng thư mục của Chuyên viên hoặc Trưởng phòng"""
        if not os.path.exists(file_path):
            return {"success": False, "message": f"File không tồn tại: {file_path}"}

        proj_data = self.cache.get("projects", {}).get(project_key)
        if not proj_data:
            # Khởi tạo dự án nếu chưa có
            self.setup_project_repository(project_key, f"Dự án {project_key}")
            proj_data = self.cache.get("projects", {}).get(project_key)

        dept = proj_data.get("departments", {}).get(dept_code)
        if not dept:
            return {"success": False, "message": f"Không tìm thấy phòng ban: {dept_code}"}

        # Tìm nhân sự tương ứng (Trưởng phòng hoặc Chuyên viên)
        target_folder_id = dept["folder_id"]
        for s_name, s_data in dept.get("staff", {}).items():
            if (is_head and ("Truong_phong" in s_name or "Founder" in s_name)) or (not is_head and "Chuyen_vien" in s_name):
                # Chọn thư mục con phù hợp nếu có
                subfolders = s_data.get("subfolders", {})
                if subfolders:
                    target_folder_id = list(subfolders.values())[0]["folder_id"]
                else:
                    target_folder_id = s_data["folder_id"]
                break

        res = self.upload_file(file_path, parent_folder_id=target_folder_id)
        return res

    def get_structure_summary(self) -> Dict[str, Any]:
        """Trả về toàn bộ cây thư mục Drive đã lập để hiển thị trên giao diện Web"""
        return {
            "connected_account": "quangvinh1302@gmail.com",
            "root_folder_name": self.root_folder_name,
            "root_folder_id": self.root_folder_id,
            "root_url": f"https://drive.google.com/drive/folders/{self.root_folder_id}",
            "projects": self.cache.get("projects", {})
        }


gdrive_connector = GoogleDriveConnector()
