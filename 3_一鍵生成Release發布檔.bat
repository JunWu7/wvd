@echo off
chcp 65001 >nul
setlocal

echo ===================================================
echo [3/3] 正在生成 Release 發布 ZIP 壓縮檔與 release.json...
echo ===================================================

python create_release_zh_tw.py
if errorlevel 1 (
    echo.
    echo [錯誤] 生成 Release 發布檔失敗！請檢查 output/wvd 是否存在。
    echo ===================================================
    pause
    exit /b 1
)

echo.
echo [成功] Release 發布檔已生成完畢！
echo ZIP 與 release.json 已準備就緒，可直接上傳至 GitHub Release/Pages。
echo ===================================================
endlocal
