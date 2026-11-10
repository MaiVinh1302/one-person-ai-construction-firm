@echo off
chcp 65001 >nul
title ĐỒNG BỘ GITHUB - CÔNG TY XÂY DỰNG 1 NGƯỜI AI (MaiVinh1302)
color 0B

echo ====================================================================
echo    CÔNG CỤ ĐỒNG BỘ DỰ ÁN LÊN GITHUB CÁ NHÂN (MaiVinh1302)
echo ====================================================================
echo.
echo Repo đích: https://github.com/MaiVinh1302/one-person-ai-construction-firm
echo.

cd /d "%~dp0"

echo [1/3] Đang kiểm tra trạng thái Git...
git status -s

echo.
set /p commit_msg="Nhập nội dung cập nhật (Bấm Enter để dùng mặc định: 'Update AI Construction Firm'): "
if "%commit_msg%"=="" set commit_msg=Update AI Construction Firm

echo.
echo [2/3] Đang lưu trữ và đóng gói commit...
git add .
git commit -m "%commit_msg%"

echo.
echo [3/3] Đang đồng bộ và đẩy mã nguồn lên GitHub...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ❌ CHÚ Ý: Chưa đẩy được lên GitHub.
    echo Lý do thông thường:
    echo 1. Bạn chưa tạo repository 'one-person-ai-construction-firm' trên GitHub:
    echo    -> Truy cập https://github.com/new và tạo repo tên 'one-person-ai-construction-firm' (Public hoặc Private).
    echo 2. Cần xác thực tài khoản:
    echo    -> Khi cửa sổ đăng nhập hiện ra, hãy chọn 'Sign in with your browser' hoặc dùng Personal Access Token (PAT).
    echo.
) else (
    echo.
    echo ✅ ĐỒNG BỘ THÀNH CÔNG LÊN GITHUB CÁ NHÂN!
    echo Truy cập repo tại: https://github.com/MaiVinh1302/one-person-ai-construction-firm
)

echo.
pause
