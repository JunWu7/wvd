import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

def sync_app_current():
    src_dir = os.path.join('app_build', 'wvd')
    dst_dir = os.path.join('app_current', 'wvd')

    if not os.path.exists(src_dir):
        print("[-] 錯誤：找不到 app_build/wvd 目錄，請先執行打包步驟！")
        sys.exit(1)

    os.makedirs(dst_dir, exist_ok=True)

    # 必須保留的個人檔案與目錄名稱
    PRESERVE_FILES = {'config.json', 'log.txt'}
    PRESERVE_DIRS = {'logs'}

    print(f"[資訊] 正在將 {src_dir} 同步至 {dst_dir} (自動保留個人 config.json 與 logs/)...")

    # 複製並覆蓋最新程式檔，但保留個人的 config.json 與 log 檔
    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(dst_dir, rel_path) if rel_path != '.' else dst_dir
        os.makedirs(target_root, exist_ok=True)

        for file in files:
            dst_file = os.path.join(target_root, file)
            # 如果是個人設定檔且目標已存在，則跳過覆蓋以保留使用者設定
            if file in PRESERVE_FILES and os.path.exists(dst_file):
                print(f"[保留] 保留現有的個人檔案: {os.path.join(rel_path, file)}")
                continue

            src_file = os.path.join(root, file)
            try:
                shutil.copy2(src_file, dst_file)
            except Exception as e:
                print(f"[-] 複製 {dst_file} 失敗: {e}")
                sys.exit(1)

    print("[+] 成功將最新版本同步至 app_current/wvd！")
    print("[+] 已完美保留您的 config.json 與歷史日誌 logs/。")

if __name__ == "__main__":
    sync_app_current()
