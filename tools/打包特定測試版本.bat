@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

echo ===================================================
echo ★ 特定版本測試包建置工具 (輸出至 app_build/ 目錄)
echo ===================================================
echo.
echo [提示] 請輸入您想要打包測試的版本號 (例如: 2.4.12 或 2.4.10)
echo.
set /p TARGET_VER=請輸入版本號 [預設 2.4.12]: 

if "%TARGET_VER%"=="" set TARGET_VER=2.4.12

echo.
echo [資訊] 正在為您開始打包指定版本 v%TARGET_VER%...
echo.

python build_custom_version.py %TARGET_VER%
if errorlevel 1 (
    echo.
    echo [錯誤] 特定版本打包失敗！
    echo ===================================================
    pause
    exit /b 1
)

echo.
echo ===================================================
echo [成功] 特定版本 v%TARGET_VER% 打包完成！位於 app_build\wvd\wvd.exe
echo ===================================================
echo.
pause
endlocal