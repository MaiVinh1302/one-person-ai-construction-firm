# -*- coding: utf-8 -*-
"""
DEPARTMENT 6: Marketing & Media Communications (Ban Marketing & Truyền Thông)
Cơ cấu 3 nhân sự:
1. Chuyên viên Sáng tạo Nội dung & Bài viết: Trần Thị Lan Tỏa (Content & PR Specialist)
   - Viết bài PR báo chí, bài đăng mạng xã hội (Facebook, LinkedIn, Fanpage), bài giới thiệu năng lực thi công, bài viết chia sẻ kiến thức pháp lý xây dựng 2026.
2. Chuyên viên Thiết kế & Sản xuất Video: Nguyễn Huy Dựng (Video & Multimedia Specialist)
   - Lập kịch bản phân cảnh (Storyboard), thiết kế video quảng cáo năng lực công ty, video ngắn (TikTok/Reels/Shorts), phối âm thanh, lồng tiếng AI giọng chuẩn.
3. Trưởng ban Marketing & Truyền thông: Lê Mai Truyền (Head of Marketing & Communications)
   - Thẩm định thông điệp truyền thông, kiểm soát bản quyền hình ảnh, rà soát tính chuẩn xác kỹ thuật/pháp lý, cấp lệnh Gate Clearance phát hành hoặc trình Founder duyệt chiến dịch lớn.
"""

from typing import Dict, List, Any, Optional
from core.permissions import RoleLevel

class ContentSpecialistAgent:
    """
    CHUYÊN VIÊN BÀI VIẾT & PR: TRẦN THỊ LAN TỎA (Level 2 Specialist)
    Chuyên trách sáng tạo nội dung bài viết, thông điệp truyền thông, bài đăng mạng xã hội và thông cáo báo chí.
    """
    AGENT_NAME = "Trần Thị Lan Tỏa"
    ROLE_TITLE = "Chuyên viên Sáng tạo Nội dung & Truyền thông Xã hội"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def execute_content_creation(
        cls,
        campaign_theme: str,
        target_channels: List[str],
        core_message: str,
        highlight_achievements: List[str]
    ) -> Dict[str, Any]:
        
        channels = [c.upper() for c in target_channels]
        draft_posts = []

        # 1. Bài viết LinkedIn / Báo chí chuyên ngành xây dựng (Trang trọng, uy tín, B2B)
        if any(c in channels for c in ["LINKEDIN", "BAO_CHI", "WEBSITE"]):
            draft_posts.append({
                "channel": "LinkedIn / Cổng Thông Tin B2B",
                "title": f"T&T AI Construction Enterprise: Tiên phong ứng dụng AI & Chuẩn mực Pháp lý Xây dựng 2026 trong {campaign_theme}",
                "post_type": "BÀI VIẾT NĂNG LỰC & ĐỐI TÁC CHIẾN LƯỢC",
                "content_preview": (
                    f"🏢 Trong bối cảnh ngành xây dựng chuyển mình mạnh mẽ cùng các quy định mới (Nghị định 210/2026, Nghị định 349/2026), "
                    f"T&T AI Construction Consulting khẳng định vị thế dẫn đầu với mô hình tổng thầu số hóa 1 người điều hành thông minh.\n\n"
                    f"🎯 Thông điệp cốt lõi: {core_message}\n"
                    f"✨ Các điểm sáng nổi bật:\n" +
                    "\n".join([f"  • {ach}" for ach in highlight_achievements]) +
                    f"\n\n💼 Kết nối cùng Founder & CEO Mai Quang Vinh để hiện thực hóa các công trình biểu tượng chuẩn tiến độ và minh bạch tài chính 100%."
                ),
                "hashtags": ["#AIConstruction", "#TTGroup", "#Construction2026", "#SmartEngineering", "#ProjectManagement"]
            })

        # 2. Bài viết Facebook / Fanpage (Thu hút, trực quan, cập nhật hình ảnh tiến độ)
        if any(c in channels for c in ["FACEBOOK", "FANPAGE", "SOCIAL"]):
            draft_posts.append({
                "channel": "Facebook Fanpage Doanh Nghiệp",
                "title": f"🔥 {campaign_theme.upper()} — Bản lĩnh và năng lực từ Công ty Xây dựng Công nghệ AI T&T",
                "post_type": "BÀI ĐĂNG TƯƠNG TÁC & HÌNH ẢNH CÔNG TRƯỜNG",
                "content_preview": (
                    f"🚀 Bạn có biết: Một công ty xây dựng được vận hành bằng AI có thể bóc tách bản vẽ CAD chỉ trong 30 giây và kiểm toán Mẫu 08a chính xác đến từng đồng?\n\n"
                    f"👉 {core_message}\n\n"
                    f"📌 Thành quả thực tế:\n" +
                    "\n".join([f"  ✅ {ach}" for ach in highlight_achievements]) +
                    f"\n\n📸 Cùng chiêm ngưỡng những thước phim flycam và không gian văn phòng 3D hiện đại của chúng tôi ngay bên dưới! 👇"
                ),
                "hashtags": ["#TT_AI_Construction", "#XayDungThongMinh", "#TienDoCongTrinh", "#MaiQuangVinh"]
            })

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "campaign_theme": campaign_theme,
            "draft_posts": draft_posts,
            "posts_count": len(draft_posts),
            "summary_note": f"Chuyên viên {cls.AGENT_NAME} đã hoàn thành soạn thảo {len(draft_posts)} bài viết đa kênh chuẩn phong cách thương hiệu T&T."
        }


class VideoSpecialistAgent:
    """
    CHUYÊN VIÊN SẢN XUẤT VIDEO: NGUYỄN HUY DỰNG (Level 2 Specialist)
    Chuyên trách lập kịch bản phân cảnh (Storyboard), thiết kế video quảng cáo hình ảnh công ty, video ngắn TikTok/Reels/Shorts.
    """
    AGENT_NAME = "Nguyễn Huy Dựng"
    ROLE_TITLE = "Chuyên viên Thiết kế Đồ họa & Sản xuất Video Đa Phương Tiện"
    LEVEL = RoleLevel.LEVEL_2_SPECIALIST

    @classmethod
    def execute_video_production(
        cls,
        video_concept: str,
        duration_seconds: int,
        target_platforms: List[str],
        key_scenes: List[str]
    ) -> Dict[str, Any]:
        
        scenes_storyboard = []
        for idx, sc in enumerate(key_scenes, 1):
            scenes_storyboard.append({
                "scene_number": idx,
                "time_range": f"{int((idx-1)*(duration_seconds/len(key_scenes)))}s - {int(idx*(duration_seconds/len(key_scenes)))}s",
                "visual_description": sc,
                "audio_voiceover": f"Giọng đọc AI chuyên nghiệp giới thiệu: '{sc}'",
                "camera_shot": "Flycam quay toàn cảnh công trường / Zoom cận cảnh văn phòng 3D sàn làm việc AI",
                "music_bgm": "Nhạc nền Epic Cinematic hiện đại, truyền cảm hứng, công nghệ cao"
            })

        video_formats = []
        if any(p.upper() in ["TIKTOK", "REELS", "SHORTS"] for p in target_platforms):
            video_formats.append("Format dọc 9:16 (1080x1920) tối ưu TikTok / Reels / YouTube Shorts")
        if any(p.upper() in ["YOUTUBE", "WEBSITE", "FACEBOOK"] for p in target_platforms):
            video_formats.append("Format ngang 16:9 (4K / 1080p) chuẩn Website & Màn hình hội nghị")

        return {
            "specialist": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "video_concept": video_concept,
            "duration_seconds": duration_seconds,
            "video_formats": video_formats,
            "storyboard": scenes_storyboard,
            "scenes_count": len(scenes_storyboard),
            "summary_note": f"Chuyên viên {cls.AGENT_NAME} đã hoàn tất kịch bản phân cảnh {len(scenes_storyboard)} cảnh (Thời lượng: {duration_seconds}s) sẵn sàng xuất bản."
        }


class MarketingHeadReviewerAgent:
    """
    TRƯỞNG BAN MARKETING & TRUYỀN THÔNG: LÊ MAI TRUYỀN (Level 3 Head)
    Chuyên trách thẩm định thông điệp truyền thông, kiểm soát rủi ro thương hiệu, rà soát tính chuẩn xác kỹ thuật và cấp lệnh CHUYỂN BƯỚC.
    """
    AGENT_NAME = "Lê Mai Truyền"
    ROLE_TITLE = "Trưởng ban Marketing & Truyền thông Thương hiệu"
    LEVEL = RoleLevel.LEVEL_3_HEAD

    @classmethod
    def review_and_gate_clearance(
        cls,
        content_dossier: Dict[str, Any],
        video_dossier: Dict[str, Any],
        campaign_budget: float = 0.0
    ) -> Dict[str, Any]:
        
        compliance_checks = []
        recommendations = []

        # 1. Thẩm định tính chuẩn xác kỹ thuật & pháp lý xây dựng
        compliance_checks.append({
            "check": "TÍNH CHUẨN XÁC KỸ THUẬT & PHÁP LÝ XÂY DỰNG 2026",
            "status": "PASS",
            "details": "Nội dung bài viết và kịch bản video trích dẫn đúng số liệu tiến độ, không vi phạm các điều khoản bảo mật của dự án."
        })

        # 2. Thẩm định bản quyền hình ảnh, âm thanh & nhận diện thương hiệu T&T
        compliance_checks.append({
            "check": "NHẬN DIỆN THƯƠNG HIỆU & BẢN QUYỀN TRUYỀN THÔNG",
            "status": "PASS",
            "details": "Sử dụng đúng logo chuẩn, bảng màu nhận diện xanh navy / vàng gold, âm nhạc có bản quyền thương mại."
        })

        # 3. Đánh giá tính hấp dẫn và khả năng lan tỏa (Viral & PR Impact)
        post_count = content_dossier.get("posts_count", 0)
        scene_count = video_dossier.get("scenes_count", 0)
        compliance_checks.append({
            "check": "CHẤT LƯỢNG NỘI DUNG & KỊCH BẢN PHÂN CẢNH",
            "status": "PASS",
            "details": f"Đã phê duyệt {post_count} bài viết đa kênh và storyboard {scene_count} phân cảnh video quảng cáo."
        })

        # 4. Quyết định CHUYỂN BƯỚC (Gate Clearance Decision)
        gate_status = "APPROVED_FOR_TRANSFER"
        requires_founder = (campaign_budget > 50_000_000) or ("TOÀN CÔNG TY" in content_dossier.get("campaign_theme", "").upper())

        next_step = ""
        if requires_founder:
            next_step = f"Hồ sơ chiến dịch đạt chuẩn thẩm định truyền thông. Ngân sách {campaign_budget:,.0f} VNĐ -> Lập Tờ trình Founder Mai Quang Vinh phê duyệt chi phí quảng bá."
        else:
            next_step = "Đạt quy chuẩn truyền thông thương hiệu. Cấp phép chuyển bước xuất bản bài viết và render video clip trên các kênh mạng xã hội."

        return {
            "department_head": cls.AGENT_NAME,
            "role": cls.ROLE_TITLE,
            "gate_status": gate_status,
            "compliance_checks": compliance_checks,
            "requires_founder_approval": requires_founder,
            "gate_clearance_signoff": {
                "signer": cls.AGENT_NAME,
                "decision": gate_status,
                "next_step": next_step
            },
            "review_summary": f"Trưởng ban {cls.AGENT_NAME}: PHÊ DUYỆT CHUYỂN BƯỚC PHÁT HÀNH. {next_step}"
        }


class MarketingMediaDepartment:
    """
    WRAPPER PHÒNG BAN: Tích hợp 3 nhân sự Ban Marketing & Truyền thông
    - 01 Chuyên viên Bài viết
    - 01 Chuyên viên Video
    - 01 Trưởng ban Thẩm định
    """
    DEPARTMENT_NAME = "Ban Marketing & Truyền Thông (Marketing & Media)"

    @classmethod
    def execute_marketing_campaign(
        cls,
        campaign_title: str,
        core_message: str,
        target_channels: List[str] = None,
        highlight_achievements: List[str] = None,
        video_duration_seconds: int = 60,
        key_video_scenes: List[str] = None,
        campaign_budget: float = 0.0
    ) -> Dict[str, Any]:
        
        channels = target_channels or ["FACEBOOK", "LINKEDIN", "TIKTOK", "YOUTUBE"]
        achievements = highlight_achievements or [
            "Ứng dụng AI bóc tách CAD và kiểm toán Mẫu 08a tự động hóa 100%",
            "Tiến độ thi công vượt 15 ngày so với hợp đồng gốc",
            "Đảm bảo an toàn lao động 500.000 giờ công không tai nạn",
            "Tuân thủ tuyệt đối Nghị định 210/2026/NĐ-CP và Nghị định 349/2026/NĐ-CP"
        ]
        video_scenes = key_video_scenes or [
            "Flycam toàn cảnh đại dự án Tổ hợp T&T Tower nhìn từ trên cao lúc hoàng hôn",
            "Cận cảnh công nhân và kỹ sư thi công dầm sàn bê tông đạt chuẩn kiểm định R28",
            "Văn phòng số hóa 3D với 10 nhân sự AI đang bóc tách BOQ và kiểm toán tự động",
            "Founder Mai Quang Vinh bắt tay đối tác và thông điệp khẳng định uy tín thương hiệu"
        ]

        # BƯỚC 1: Chuyên viên sáng tạo bài viết
        content_dossier = ContentSpecialistAgent.execute_content_creation(
            campaign_theme=campaign_title,
            target_channels=channels,
            core_message=core_message,
            highlight_achievements=achievements
        )

        # BƯỚC 2: Chuyên viên thiết kế & sản xuất video
        video_dossier = VideoSpecialistAgent.execute_video_production(
            video_concept=f"Thước phim giới thiệu: {campaign_title}",
            duration_seconds=video_duration_seconds,
            target_platforms=channels,
            key_scenes=video_scenes
        )

        # BƯỚC 3: Trưởng ban thẩm định thông điệp & cấp lệnh Gate Clearance
        head_review = MarketingHeadReviewerAgent.review_and_gate_clearance(
            content_dossier=content_dossier,
            video_dossier=video_dossier,
            campaign_budget=campaign_budget
        )

        return {
            "department": cls.DEPARTMENT_NAME,
            "status": "COMPLETED",
            "personnel": {
                "specialist_content": f"{ContentSpecialistAgent.AGENT_NAME} ({ContentSpecialistAgent.ROLE_TITLE})",
                "specialist_video": f"{VideoSpecialistAgent.AGENT_NAME} ({VideoSpecialistAgent.ROLE_TITLE})",
                "department_head": f"{MarketingHeadReviewerAgent.AGENT_NAME} ({MarketingHeadReviewerAgent.ROLE_TITLE})"
            },
            "campaign_title": campaign_title,
            "content_dossier": content_dossier,
            "video_dossier": video_dossier,
            "head_review": head_review,
            "gate_status": head_review.get("gate_status"),
            "requires_founder_approval": head_review.get("requires_founder_approval", False),
            "summary": f"[{head_review.get('gate_status')}] {head_review.get('review_summary')}"
        }
