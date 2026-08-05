@echo off
chcp 65001 >nul
setlocal

echo [資訊] 正在清理舊的構建檔案...
python -c "import shutil, os, glob; shutil.rmtree('output', ignore_errors=True); shutil.rmtree('dist', ignore_errors=True); shutil.rmtree('build', ignore_errors=True); [os.remove(f) for f in glob.glob('*.spec')]"

echo [1/3] 正在準備繁體化臨時源碼副本...
python update_zh_tw.py

echo [2/3] 開始一鍵打包繁體中文版 WvDAS 到 output/ 目錄...
python -m PyInstaller --onedir -y --noconfirm --distpath output --add-data "resources;resources/" --add-data "locale;locale/" --add-data "CHANGES_LOG.md;." build/src_patched/main.py -n wvd

if errorlevel 1 (
    echo.
    echo [錯誤] 打包失敗！請檢查上方錯誤訊息。
    echo ===================================================
    pause
    exit /b 1
)

echo [3/3] 正在修補打包檔的動態資源與更新日誌...
python update_zh_tw.py

echo [資訊] 正在清理 build 臨時快取資料夾...
python -c "import shutil; shutil.rmtree('build', ignore_errors=True)"

echo.
echo ===================================================
echo [成功] 繁體中文版已成功打包完成！
echo 可執行檔位於: output\wvd\wvd.exe
echo ===================================================
echo.
pause
endlocal
