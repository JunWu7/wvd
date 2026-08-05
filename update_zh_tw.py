import os
import sys
import json
import struct
import shutil
import re

try:
    import opencc
    converter = opencc.OpenCC('s2t')
    def s2t(text):
        if not text:
            return text
        return converter.convert(text)
except ImportError:
    def s2t(text):
        return text

def ensure_config_zh_tw():
    main_file = os.path.join('src', 'main.py')
    ver_str = '2.4.13'
    if os.path.exists(main_file):
        try:
            with open(main_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip().startswith('__version__'):
                        ver_str = line.split('=')[1].strip().strip("'\"")
                        break
        except Exception:
            pass

    possible_files = [
        os.path.join('app_build', 'wvd', 'config.json'),
        os.path.join('output', 'wvd', 'config.json')
    ]
    for config_file in possible_files:
        dst_dir = os.path.dirname(config_file)
        if not os.path.exists(dst_dir):
            continue
        try:
            data = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            if 'GENERAL' not in data or not isinstance(data['GENERAL'], dict):
                data['GENERAL'] = {}
            data['GENERAL']['LANGUAGE'] = 'zh_TW'
            data['GENERAL']['LAST_VERSION'] = ver_str
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[+] 已確保 {config_file} 設定為 GENERAL.LANGUAGE = 'zh_TW', LAST_VERSION = '{ver_str}'")
        except Exception as e:
            print(f"[-] 設定 {config_file} 失敗: {e}")

def prepare_patched_src():
    """ 複製 src/ 到 build/src_patched/ 並對 .py 檔案內的簡體中文進行 OpenCC 轉換，同時修正更新源與重啟腳本編碼 """
    src_dir = 'src'
    build_dir = os.path.join('build', 'src_patched')
    
    if not os.path.exists(src_dir):
        print("[-] 未找到 src 目錄！")
        return False
        
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
        
    os.makedirs(build_dir, exist_ok=True)
    
    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(build_dir, rel_path) if rel_path != '.' else build_dir
        os.makedirs(target_root, exist_ok=True)
        
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_root, file)
            
            if file.endswith('.py'):
                try:
                    with open(src_file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                    
                    tw_code_content = s2t(code_content)
                    
                    if file == 'main.py':
                        tw_code_content = tw_code_content.replace('OWNER = "arnold2957"', 'OWNER = "JunWu7"')
                        
                    if file == 'auto_updater.py':
                        tw_code_content = tw_code_content.replace(
                            'with open("_update_restart.bat", "w") as f:',
                            'with open("_update_restart.bat", "w", encoding="utf-8") as f:'
                        )
                        tw_code_content = tw_code_content.replace(
                            'with open("_update_restart.sh", "w") as f:',
                            'with open("_update_restart.sh", "w", encoding="utf-8") as f:'
                        )
                        new_script_block = '''script = f"""@echo off
chcp 65001 >nul
REM Waiting for main process exit
timeout /t 2 /nobreak >nul

REM Copy unpacked files
xcopy /E /Y /Q "{unpack_dir}\\\\*" "."

REM Restart main executable
start "" "{os.path.basename(sys.argv[0])}"

REM Clean temporary update folder
rmdir /S /Q "__update_temp__"

REM Delete restart script
del "%~f0"
    """'''
                        tw_code_content, _ = re.subn(
                            r'script = f"""@echo off.*?del "%~f0"\s*"""',
                            new_script_block,
                            tw_code_content,
                            flags=re.DOTALL
                        )

                    with open(dst_file, 'w', encoding='utf-8') as f:
                        f.write(tw_code_content)
                except Exception as e:
                    print(f"[-] 轉換 {src_file} 時發生錯誤: {e}，複製原檔")
                    shutil.copy2(src_file, dst_file)
            else:
                shutil.copy2(src_file, dst_file)
                
    print(f"[+] 已成功在 build/ 建立修補與注入更新源的臨時源碼目錄: {build_dir}")
    return True

def patch_output_quest_json():
    """ 僅修補 app_build 與 output 中的 quest.json 原地欄位，避免產生 FarmQuest 白名單警告 """
    possible_paths = [
        os.path.join('app_build', 'wvd', '_internal', 'resources', 'quest', 'quest.json'),
        os.path.join('app_build', 'wvd', 'resources', 'quest', 'quest.json'),
        os.path.join('output', 'wvd', '_internal', 'resources', 'quest', 'quest.json'),
        os.path.join('output', 'wvd', 'resources', 'quest', 'quest.json')
    ]
    
    patched_count = 0
    for quest_file in possible_paths:
        if not os.path.exists(quest_file):
            continue
        
        try:
            with open(quest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            modified = False
            for quest_code, quest_info in data.items():
                if isinstance(quest_info, dict):
                    if 'questName' in quest_info:
                        quest_info['questName'] = s2t(quest_info['questName'])
                        modified = True
                    if 'questCategory' in quest_info:
                        quest_info['questCategory'] = s2t(quest_info['questCategory'])
                        modified = True
                    if '_TIPS' in quest_info and isinstance(quest_info['_TIPS'], str):
                        quest_info['_TIPS'] = s2t(quest_info['_TIPS'])
                        modified = True

            if modified:
                with open(quest_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"[+] 已成功對打包產物 {quest_file} (questName, questCategory, _TIPS) 進行原地繁體轉換！")
                patched_count += 1
        except Exception as e:
            print(f"[-] 修補 {quest_file} 時發生錯誤: {e}")

    if patched_count == 0:
        print("[!] 尚未發現 output 目錄下的 quest.json（將在打包完成後自動修補）")

def patch_output_changes_log():
    """ 讀取原始 CHANGES_LOG.md，轉為繁體後寫入 output 打包目錄 """
    src_log = 'CHANGES_LOG.md'
    if not os.path.exists(src_log):
        print(f"[!] 未找到原始 {src_log}，跳過繁體日誌複製")
        return
    
    try:
        with open(src_log, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tw_content = s2t(content)
        
        possible_paths = [
            os.path.join('app_build', 'wvd', 'CHANGES_LOG.md'),
            os.path.join('app_build', 'wvd', '_internal', 'CHANGES_LOG.md'),
            os.path.join('output', 'wvd', 'CHANGES_LOG.md'),
            os.path.join('output', 'wvd', '_internal', 'CHANGES_LOG.md')
        ]
        
        for dst_path in possible_paths:
            dst_dir = os.path.dirname(dst_path)
            if os.path.exists(dst_dir):
                with open(dst_path, 'w', encoding='utf-8') as f:
                    f.write(tw_content)
                print(f"[+] 已成功將繁體更新日誌寫入打包產物: {dst_path}")
    except Exception as e:
        print(f"[-] 處理 CHANGES_LOG.md 時發生錯誤: {e}")

def parse_po(po_filepath):
    if not os.path.exists(po_filepath):
        return []
    
    entries = []
    current_comments = []
    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False

    with open(po_filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line_str = line.rstrip('\r\n')
        if line_str.startswith('#'):
            if current_msgid is not None:
                entries.append((current_comments, current_msgid, current_msgstr))
                current_comments = []
                current_msgid = None
                current_msgstr = None
                in_msgid = False
                in_msgstr = False
            current_comments.append(line_str)
        elif line_str.startswith('msgid '):
            if current_msgid is not None:
                entries.append((current_comments, current_msgid, current_msgstr))
                current_comments = []
                current_msgstr = None
            current_msgid = line_str[6:].strip('"')
            in_msgid = True
            in_msgstr = False
        elif line_str.startswith('msgstr '):
            current_msgstr = line_str[7:].strip('"')
            in_msgid = False
            in_msgstr = True
        elif line_str.startswith('"') and line_str.endswith('"'):
            content = line_str[1:-1]
            if in_msgid and current_msgid is not None:
                current_msgid += content
            elif in_msgstr and current_msgstr is not None:
                current_msgstr += content
        elif line_str == '':
            if current_msgid is not None:
                entries.append((current_comments, current_msgid, current_msgstr))
                current_comments = []
                current_msgid = None
                current_msgstr = None
                in_msgid = False
                in_msgstr = False

    if current_msgid is not None:
        entries.append((current_comments, current_msgid, current_msgstr))

    return entries

def unescape(s):
    return s.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')

def escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')

def generate_zh_tw_po():
    zh_cn_po = os.path.join('locale', 'zh_CN', 'LC_MESSAGES', 'messages.po')
    zh_tw_dir = os.path.join('locale', 'zh_TW', 'LC_MESSAGES')
    os.makedirs(zh_tw_dir, exist_ok=True)
    zh_tw_po = os.path.join(zh_tw_dir, 'messages.po')

    cn_entries = parse_po(zh_cn_po)
    tw_entries_existing = parse_po(zh_tw_po) if os.path.exists(zh_tw_po) else []
    
    existing_tw_map = {}
    for comments, msgid, msgstr in tw_entries_existing:
        if msgid:
            existing_tw_map[msgid] = msgstr

    new_tw_lines = []

    for comments, msgid, msgstr in cn_entries:
        for c in comments:
            new_tw_lines.append(c + '\n')
        
        if msgid == "":
            tw_header = (
                'msgid ""\n'
                'msgstr ""\n'
                '"Project-Id-Version: PROJECT VERSION\\n"\n'
                '"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"\n'
                '"POT-Creation-Date: 2026-06-25 20:51+0800\\n"\n'
                '"PO-Revision-Date: 2026-08-05 18:00+0800\\n"\n'
                '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n'
                '"Language: zh_TW\\n"\n'
                '"Language-Team: zh_TW <LL@li.org>\\n"\n'
                '"Plural-Forms: nplurals=1; plural=0;\\n"\n'
                '"MIME-Version: 1.0\\n"\n'
                '"Content-Type: text/plain; charset=utf-8\\n"\n'
                '"Content-Transfer-Encoding: 8bit\\n"\n'
                '"Generated-By: Babel 2.11.0\\n"\n\n'
            )
            new_tw_lines.append(tw_header)
            continue

        raw_msgid = unescape(msgid)
        final_msgstr = escape(s2t(raw_msgid))

        new_tw_lines.append(f'msgid "{msgid}"\n')
        new_tw_lines.append(f'msgstr "{final_msgstr}"\n\n')

    with open(zh_tw_po, 'w', encoding='utf-8') as f:
        f.writelines(new_tw_lines)

    print(f"[+] 已使用 OpenCC 成功生成/更新 {zh_tw_po}")

def compile_po_to_mo(po_path, mo_path):
    entries = parse_po(po_path)
    messages = {
        b"": b"Content-Type: text/plain; charset=utf-8\n"
    }
    
    for comments, msgid, msgstr in entries:
        if msgid == "":
            continue
        raw_id = unescape(msgid)
        raw_str = unescape(msgstr) if (msgstr and msgstr.strip()) else s2t(raw_id)
        if raw_id:
            messages[raw_id.encode('utf-8')] = raw_str.encode('utf-8')

    keys = sorted(messages.keys())
    ids = []
    strs = []
    
    for k in keys:
        ids.append(k)
        strs.append(messages[k])

    N = len(keys)
    keystart = 28 + N * 16
    valstart = keystart + sum(len(k) + 1 for k in ids)
    
    id_offsets = []
    curr_k = keystart
    for k in ids:
        l = len(k)
        id_offsets.append((l, curr_k))
        curr_k += l + 1
        
    val_offsets = []
    curr_v = valstart
    for v in strs:
        l = len(v)
        val_offsets.append((l, curr_v))
        curr_v += l + 1

    offsets = id_offsets + val_offsets
    
    header = struct.pack("IIIIIII", 
                         0x950412de, # Magic
                         0,          # Version
                         N,          # Number of entries
                         28,         # Offset of Orig table
                         28 + N * 8, # Offset of Trans table
                         0, 0)       # Hash table size & offset

    os.makedirs(os.path.dirname(mo_path), exist_ok=True)
    with open(mo_path, "wb") as f:
        f.write(header)
        for l, o in offsets:
            f.write(struct.pack("II", l, o))
        for k in ids:
            f.write(k + b"\x00")
        for v in strs:
            f.write(v + b"\x00")

    print(f"[+] 已成功編譯 {mo_path}")

def main():
    print("=== 開始一鍵繁體翻譯與語系更新 ===")
    ensure_config_zh_tw()
    generate_zh_tw_po()
    
    zh_tw_po = os.path.join('locale', 'zh_TW', 'LC_MESSAGES', 'messages.po')
    zh_tw_mo = os.path.join('locale', 'zh_TW', 'LC_MESSAGES', 'messages.mo')
    compile_po_to_mo(zh_tw_po, zh_tw_mo)
    
    zh_cn_po = os.path.join('locale', 'zh_CN', 'LC_MESSAGES', 'messages.po')
    zh_cn_mo = os.path.join('locale', 'zh_CN', 'LC_MESSAGES', 'messages.mo')
    if os.path.exists(zh_cn_po):
        compile_po_to_mo(zh_cn_po, zh_cn_mo)

    en_us_po = os.path.join('locale', 'en_US', 'LC_MESSAGES', 'messages.po')
    en_us_mo = os.path.join('locale', 'en_US', 'LC_MESSAGES', 'messages.mo')
    if os.path.exists(en_us_po):
        compile_po_to_mo(en_us_po, en_us_mo)

    prepare_patched_src()
    patch_output_quest_json()
    patch_output_changes_log()

    print("=== 繁體語系更新與編譯完成！ ===")

if __name__ == "__main__":
    main()
