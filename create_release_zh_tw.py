import os
import sys
import json
import hashlib
import zipfile

def get_current_version():
    config_file = os.path.join('output', 'wvd', 'config.json')
    if not os.path.exists(config_file):
        config_file = 'config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('GENERAL', {}).get('LAST_VERSION', '2.4.12')
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
    out_dir = os.path.join('output', 'wvd')
    if not os.path.exists(out_dir):
        print(f"[-] 錯誤：找不到打包成品目錄 {out_dir}，請先執行打包步驟！")
        return None, None
    
    release_dir = 'release_zip'
    os.makedirs(release_dir, exist_ok=True)
    
    zip_filename = f"wvd_zh_TW_v{version}.zip"
    zip_filepath = os.path.join(release_dir, zip_filename)
    
    print(f"[+] 正在將 {out_dir} 打包壓縮為 {zip_filepath}...")
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(out_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, out_dir)
                zipf.write(abs_path, rel_path)
                
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
    
    release_json_path = "release.json"
    with open(release_json_path, 'w', encoding='utf-8') as f:
        json.dump(release_data, f, ensure_ascii=False, indent=4)
        
    print(f"[+] 已成功生成專屬發布檔: {release_json_path}")
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
