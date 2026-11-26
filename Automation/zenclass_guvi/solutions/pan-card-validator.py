import sys
import re

def main():
    s = sys.stdin.readline().strip()
    if re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', s):
        print('pan')
    else:
        print('not pan')

if __name__ == '__main__':
    main()
