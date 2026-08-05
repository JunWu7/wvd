@echo off
chcp 65001 >nul
setlocal

echo ===================================================
echo [1/3] 正在拉取 upstream 上游最新代碼...
echo ===================================================

git fetch upstream
if errorlevel 1 (
    echo.
    echo [錯誤] 抓取 upstream 上游更新失敗！請檢查網路連線或 Git 設定。
    echo ===================================================
    pause
    exit /b 1
)

git merge upstream/master
if errorlevel 1 (
    echo.
    echo [錯誤] 合併 upstream/master 時發生衝突 (Conflict)！請先手動解決衝突。
    echo ===================================================
    pause
    exit /b 1
)

echo.
echo [成功] 已成功拉取並合併上游最新代碼！
echo ===================================================
endlocal
