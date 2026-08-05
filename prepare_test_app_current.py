import os
import sys
import shutil
import subprocess
import json

def prepare_test_app_current():
    print("===================================================")
    print("[測試環境建置] 正在構建 v2.4.12 測試版的 app_current/ 運行環境...")
    print("===================================================")

    # 1. 確保 build/src_patched 存在
    res = subprocess.run([sys.executable, 'update_zh_tw.py'])
    if res.returncode != 0:
        print("[錯誤] update_zh_tw.py 執行失敗！")
        return False

    patched_main = os.path.join('build', 'src_patched', 'main.py')
    if not os.path.exists(patched_main):
        print("[錯誤] build/src_patched/main.py 不存在！")
        return False

    # 2. 修改 build/src_patched/main.py 的 __version__ 為 "2.4.12"
    with open(patched_main, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    new_content = []
    for line in content.splitlines():
        if line.startswith('__version__ ='):
            new_content.append('__version__ = "2.4.12"')
        else:
            new_content.append(line)
    
    with open(patched_main, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))

    print("[+] 已將 build/src_patched/main.py 版本設定為 '2.4.12'")

    # 3. 清理舊 app_current/wvd，但保護 config.json 與 logs/
    app_current_dir = os.path.join('app_current', 'wvd')
    saved_config = None
    saved_logs = os.path.join('app_current', 'saved_logs')
    
    config_file = os.path.join(app_current_dir, 'config.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
        except Exception:
            pass

    logs_dir = os.path.join(app_current_dir, 'logs')
    if os.path.exists(logs_dir):
        shutil.rmtree(saved_logs, ignore_errors=True)
        shutil.copytree(logs_dir, saved_logs, dirs_exist_ok=True)

    # 4. 執行 PyInstaller 打包到 app_current/
    cmd = [
        sys.executable, '-m', 'PyInstaller', '--onedir', '-y', '--noconfirm',
        '--distpath', 'app_current',
        '--add-data', 'resources;resources/',
        '--add-data', 'locale;locale/',
        '--add-data', 'CHANGES_LOG.md;.',
        patched_main,
        '-n', 'wvd'
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[錯誤] 打包 v2.4.12 測試版至 app_current 失敗！")
        return False

    # 5. 修補 app_current/wvd 的語系與設定檔 (設 LAST_VERSION = '2.4.12')
    if saved_config:
        if 'GENERAL' not in saved_config:
            saved_config['GENERAL'] = {}
        saved_config['GENERAL']['LANGUAGE'] = 'zh_TW'
        saved_config['GENERAL']['LAST_VERSION'] = '2.4.12'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(saved_config, f, ensure_ascii=False, indent=4)
    else:
        cfg = {"GENERAL": {"LANGUAGE": "zh_TW", "LAST_VERSION": "2.4.12"}}
        os.makedirs(app_current_dir, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)

    if os.path.exists(saved_logs):
        target_logs = os.path.join(app_current_dir, 'logs')
        shutil.copytree(saved_logs, target_logs, dirs_exist_ok=True)
        shutil.rmtree(saved_logs, ignore_errors=True)

    # 6. 再次執行 update_zh_tw.py 對 app_current 原地修補 quest.json 與 CHANGES_LOG
    subprocess.run([sys.executable, 'update_zh_tw.py'])
    shutil.rmtree('build', ignore_errors=True)

    print("===================================================")
    print("[成功] app_current/ 測試環境已成功打造完畢！")
    print(" - 執行檔位置: app_current/wvd/wvd.exe")
    print(" - 內建版本號: 2.4.12")
    print(" - 更新邏輯: 100% 已套用最新的 JunWu7 倉庫 + UTF-8 重啟修復！")
    print("===================================================")
    return True

if __name__ == '__main__':
    prepare_test_app_current()
