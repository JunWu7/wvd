@echo off
chcp 65001 >nul
setlocal

echo ===================================================
echo ★ 開始全自動一鍵流程：拉取 -> 繁體打包 -> 發布檔生成
echo ===================================================
echo.

call "1_拉取上游最新代碼.bat"
if errorlevel 1 (
    echo.
    echo [中斷] 步驟 1 (拉取上游代碼) 失敗，流程已終止。
    echo ===================================================
    pause
    exit /b 1
)

echo.
call "2_一鍵更新翻譯與打包.bat"
if errorlevel 1 (
    echo.
    echo [中斷] 步驟 2 (繁體更新與打包) 失敗，流程已終止。
    echo ===================================================
    pause
    exit /b 1
)

echo.
call "3_一鍵生成Release發布檔.bat"
if errorlevel 1 (
    echo.
    echo [中斷] 步驟 3 (生成 Release 發布檔) 失敗，流程已終止。
    echo ===================================================
    pause
    exit /b 1
)

echo.
echo ===================================================
echo  全部流程 100%% 成功完成！
echo 1. 最新上游代碼已拉取
echo 2. 繁體中文版已打包至 output\wvd\wvd.exe
echo 3. 發布檔已生成 (release.json 與 release_zip/ 目錄)
echo ===================================================
echo.
pause
endlocal
