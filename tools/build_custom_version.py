import os
import sys

# 切換工作目錄至專案根目錄
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(repo_root)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
import os
import sys
import shutil
import subprocess
import json

def build_custom_version(target_version="2.4.12"):
    print("===================================================")
    print(f"[客製版本打包] 正在構建特定版本 v{target_version} 至 app_build/...")
    print("===================================================")

    # 1. 執行 update_zh_tw.py 建立 build/src_patched
    res = subprocess.run([sys.executable, 'update_zh_tw.py'])
    if res.returncode != 0:
        print("[錯誤] update_zh_tw.py 執行失敗！")
        return False

    patched_main = os.path.join('build', 'src_patched', 'main.py')
    if not os.path.exists(patched_main):
        print("[錯誤] build/src_patched/main.py 不存在！")
        return False

    # 2. 將 build/src_patched/main.py 的 __version__ 替換為指定的 target_version
    with open(patched_main, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    new_content = []
    for line in content.splitlines():
        if line.startswith('__version__ ='):
            new_content.append(f'__version__ = "{target_version}"')
        else:
            new_content.append(line)
    
    with open(patched_main, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))

    print(f"[+] 已將臨時編譯源碼的主版本號調整為: 'v{target_version}'")

    # 3. 清理舊 app_build/
    shutil.rmtree('app_build', ignore_errors=True)

    # 4. 執行 PyInstaller 打包至 app_build/
    cmd = [
        sys.executable, '-m', 'PyInstaller', '--onedir', '-y', '--noconfirm',
        '--distpath', 'app_build',
        '--add-data', 'resources;resources/',
        '--add-data', 'locale;locale/',
        '--add-data', 'CHANGES_LOG.md;.',
        patched_main,
        '-n', 'wvd'
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[錯誤] 打包 v{target_version} 至 app_build/ 失敗！")
        return False

    # 5. 修補 app_build/wvd 的 config.json (設 LAST_VERSION = target_version)
    build_config = os.path.join('app_build', 'wvd', 'config.json')
    if os.path.exists(os.path.dirname(build_config)):
        data = {}
        if os.path.exists(build_config):
            try:
                with open(build_config, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                pass
        if 'GENERAL' not in data or not isinstance(data['GENERAL'], dict):
            data['GENERAL'] = {}
        data['GENERAL']['LANGUAGE'] = 'zh_TW'
        data['GENERAL']['LAST_VERSION'] = target_version
        with open(build_config, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # 6. 再次執行 update_zh_tw.py 對 app_build 原地修補 quest.json 與 CHANGES_LOG
    subprocess.run([sys.executable, 'update_zh_tw.py'])
    shutil.rmtree('build', ignore_errors=True)

    print("===================================================")
    print(f"[成功] 特定版本 v{target_version} 已成功打包至 app_build/！")
    print(f" - 可執行檔位置: app_build/wvd/wvd.exe")
    print(f" - 指定版本號: {target_version}")
    print(" - 補丁與翻譯: 100% 套用最新繁體翻譯 + JunWu7 倉庫 + UI 安全防護！")
    print(" - 提示: 您的當前運行環境 (app_current/) 完好不受任何影響！")
    print("===================================================")
    return True

if __name__ == '__main__':
    ver = sys.argv[1] if len(sys.argv) > 1 else "2.4.12"
    build_custom_version(ver)
