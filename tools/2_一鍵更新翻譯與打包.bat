@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

python tools\check_pipeline.py 2
if errorlevel 1 (
    echo.
    echo [錯誤] 步驟 2 執行失敗！
    echo ===================================================
    if not "%~1"=="--no-pause" pause
    exit /b 1
)

if not "%~1"=="--no-pause" pause
endlocal