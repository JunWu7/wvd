@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

python tools\sync_app_current.py
if errorlevel 1 (
    echo.
    echo [錯誤] 同步至 app_current 失敗！請檢查 app_current\wvd\wvd.exe 是否正被開啟使用中。
    echo ===================================================
    if not "%~1"=="--no-pause" pause
    exit /b 1
)

if not "%~1"=="--no-pause" pause
endlocal