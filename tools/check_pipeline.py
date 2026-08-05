import os
import sys

# 切換工作目錄至專案根目錄
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(repo_root)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
import os
import sys
import json
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

def get_file_version(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip().startswith('__version__'):
                    return line.split('=')[1].strip().strip("'\"")
    except Exception:
        pass
    return None

def get_json_version(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            if isinstance(data, dict):
                if 'version' in data:
                    return data.get('version')
                if 'GENERAL' in data and isinstance(data['GENERAL'], dict):
                    return data['GENERAL'].get('LAST_VERSION') or data['GENERAL'].get('LATEST_VERSION')
    except Exception:
        pass
    return None

def parse_version(ver_str):
    if not ver_str:
        return (0, 0, 0)
    clean_ver = ver_str.split('-')[0]
    parts = clean_ver.split('.')
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])

def run_step_1():
    print("===================================================")
    print("[1/3] 檢查與拉取 upstream 上游最新代碼...")
    print("===================================================")
    
    # 取得本地 src/main.py 版本
    local_ver_str = get_file_version(os.path.join('src', 'main.py')) or '0.0.0'
    local_ver = parse_version(local_ver_str)
    
    # 執行 git fetch upstream
    try:
        subprocess.run(['git', 'fetch', 'upstream'], check=True, capture_output=True)
    except Exception as e:
        print(f"[!] 抓取 upstream 失敗或無網絡，將使用本地代碼繼續 ({e})")
        return
        
    # 讀取 upstream/master 的 src/main.py 版本
    upstream_ver_str = None
    try:
        res = subprocess.run(['git', 'show', 'upstream/master:src/main.py'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if line.strip().startswith('__version__'):
                    upstream_ver_str = line.split('=')[1].strip().strip("'\"")
                    break
    except Exception:
        pass

    upstream_ver = parse_version(upstream_ver_str) if upstream_ver_str else (0, 0, 0)

    # 比較版本
    if upstream_ver <= local_ver and upstream_ver != (0,0,0):
        print(f"[跳過] 上游代碼 (v{upstream_ver_str or local_ver_str}) 沒有更新的版本，跳過步驟 1 拉取。")
        return
        
    print(f"[資訊] 發現上游新版本 (v{upstream_ver_str})，正在執行合併...")
    res = subprocess.run(['git', 'merge', 'upstream/master', '--no-edit'])
    if res.returncode != 0:
        print("[錯誤] 合併 upstream/master 發生衝突！請手動解決衝突。")
        sys.exit(1)
    print("[成功] 已成功拉取並合併上游最新代碼！")

def run_step_2():
    print("===================================================")
    print("[2/3] 檢查與執行繁體語系更新與一鍵打包...")
    print("===================================================")
    
    local_ver_str = get_file_version(os.path.join('src', 'main.py')) or '2.4.13'
    build_exe = os.path.join('app_build', 'wvd', 'wvd.exe')
    build_config = os.path.join('app_build', 'wvd', 'config.json')
    build_ver_str = get_json_version(build_config)
    
    # 檢查 app_build/ 是否已經是最新版且產物完整
    if os.path.exists(build_exe) and build_ver_str == local_ver_str:
        print(f"[跳過] app_build/ 打包成品已是最新版本 (v{local_ver_str})，跳過重複打包。")
        return

    print(f"[資訊] 正在為版本 v{local_ver_str} 執行繁體轉換與 PyInstaller 打包...")
    
    # 清理舊構建
    shutil.rmtree('app_build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree('build', ignore_errors=True)

    # 執行 update_zh_tw.py
    res = subprocess.run([sys.executable, 'update_zh_tw.py'])
    if res.returncode != 0:
        print("[錯誤] 繁體語系更新失敗！")
        sys.exit(1)

    # 執行 PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller', '--onedir', '-y', '--noconfirm',
        '--distpath', 'app_build',
        '--add-data', 'resources;resources/',
        '--add-data', 'locale;locale/',
        '--add-data', 'CHANGES_LOG.md;.',
        os.path.join('build', 'src_patched', 'main.py'),
        '-n', 'wvd'
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[錯誤] PyInstaller 打包失敗！")
        sys.exit(1)

    # 修補動態資源與清理
    subprocess.run([sys.executable, 'update_zh_tw.py'])
    shutil.rmtree('build', ignore_errors=True)

    print(f"[成功] 繁體中文版已成功打包至 app_build/wvd/wvd.exe (v{local_ver_str})！")

def run_step_3():
    print("===================================================")
    print("[3/3] 檢查與生成 Release 發布包...")
    print("===================================================")
    
    local_ver_str = get_file_version(os.path.join('src', 'main.py')) or '2.4.13'
    release_json_path = os.path.join('app_release', 'release.json')
    release_zip_path = os.path.join('app_release', f'wvd_zh_TW_v{local_ver_str}.zip')
    release_ver_str = get_json_version(release_json_path)

    # 檢查 app_release/ 是否已經存在最新發布檔
    if os.path.exists(release_zip_path) and release_ver_str == local_ver_str:
        print(f"[跳過] app_release/ 發布包已是最新版本 (v{local_ver_str})，跳過重複生成。")
        return

    print(f"[資訊] 正在生成 v{local_ver_str} 的 Release 發布 ZIP 壓縮檔與 release.json...")
    res = subprocess.run([sys.executable, 'create_release_zh_tw.py'])
    if res.returncode != 0:
        print("[錯誤] 生成 Release 發布檔失敗！")
        sys.exit(1)

    print(f"[成功] Release 發布包已生成於 app_release/ (v{local_ver_str})！")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        step = sys.argv[1]
        if step == '1':
            run_step_1()
        elif step == '2':
            run_step_2()
        elif step == '3':
            run_step_3()
    else:
        run_step_1()
        run_step_2()
        run_step_3()
