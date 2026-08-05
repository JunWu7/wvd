import sys
from build_custom_version import build_custom_version

if __name__ == '__main__':
    ver = sys.argv[1] if len(sys.argv) > 1 else "2.4.12"
    build_custom_version(ver)
