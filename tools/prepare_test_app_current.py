import os
import sys

# 切換工作目錄至專案根目錄
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(repo_root)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
import sys
from build_custom_version import build_custom_version

if __name__ == '__main__':
    ver = sys.argv[1] if len(sys.argv) > 1 else "2.4.12"
    build_custom_version(ver)
