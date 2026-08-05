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
import hashlib
import shutil
import zipfile

def get_current_version():
    # 1. 優先從 src/main.py 或 build/src_patched/main.py 自動讀取原作者定義的 __version__
    main_files = [
        os.path.join('build', 'src_patched', 'main.py'),
        os.path.join('src', 'main.py')
    ]
    for main_file in main_files:
        if os.path.exists(main_file):
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('__version__'):
                            ver = line.split('=')[1].strip().strip("'\"")
                            if ver:
                                return ver
            except Exception:
                pass

    # 2. 備份：從打包產物的 config.json 讀取
    config_files = [
        os.path.join('app_build', 'wvd', 'config.json'),
        os.path.join('output', 'wvd', 'config.json'),
        'config.json'
    ]
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ver = data.get('GENERAL', {}).get('LAST_VERSION')
                    if ver:
                        return ver
            except Exception:
                pass
    return '2.4.12'

def compute_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def make_release_zip(version):
    out_dir = os.path.join('app_build', 'wvd')
    if not os.path.exists(out_dir):
        out_dir = os.path.join('output', 'wvd')
    
    if not os.path.exists(out_dir):
        print(f"[-] 錯誤：找不到打包成品目錄 (app_build/wvd)，請先執行打包步驟！")
        return None, None
    
    release_dir = 'app_release'
    if os.path.exists(release_dir):
        print(f"[資訊] 正在自動清空舊的發布目錄 {release_dir}...")
        shutil.rmtree(release_dir, ignore_errors=True)
        
    os.makedirs(release_dir, exist_ok=True)
    
    zip_filename = f"wvd_zh_TW_v{version}.zip"
    zip_filepath = os.path.join(release_dir, zip_filename)
    
    print(f"[+] 正在將 {out_dir} 打包壓縮為 {zip_filepath}...")
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(out_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                if not os.path.exists(abs_path):
                    continue
                rel_path = os.path.relpath(abs_path, out_dir)
                try:
                    zipf.write(abs_path, rel_path)
                except FileNotFoundError:
                    pass
                
    md5_value = compute_md5(zip_filepath)
    print(f"[+] 壓縮完成！MD5 校驗碼: {md5_value}")
    return zip_filepath, md5_value

def generate_release_json(version, zip_filename, md5_value, github_user="JunWu7", github_repo="wvd"):
    download_url = f"https://github.com/{github_user}/{github_repo}/releases/download/v{version}/{zip_filename}"
    release_data = {
        "version": version,
        "download_url": download_url,
        "md5": md5_value
    }
    
    # 同時寫入 app_release/release.json 與 根目錄 release.json
    paths = [
        os.path.join("app_release", "release.json"),
        "release.json"
    ]
    
    for p in paths:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(release_data, f, ensure_ascii=False, indent=4)
        print(f"[+] 已成功生成發布檔: {p}")
        
    print("=" * 50)
    print(json.dumps(release_data, ensure_ascii=False, indent=4))
    print("=" * 50)

def main():
    print("=== 開始一鍵生成 Release 發布檔 ===")
    version = get_current_version()
    print(f"[+] 當前發布版本號: v{version}")
    
    zip_path, md5_value = make_release_zip(version)
    if not zip_path or not md5_value:
        sys.exit(1)
        
    zip_filename = os.path.basename(zip_path)
    generate_release_json(version, zip_filename, md5_value)
    print("=== Release 發布檔生成完畢！ ===")

if __name__ == "__main__":
    main()

