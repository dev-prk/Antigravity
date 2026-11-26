import sys

def main():
    s = sys.stdin.readline()
    if s.endswith('\n'):
        s = s[:-1]
    if s.endswith('\r'):
        s = s[:-1]
    for ch in s:
        print(ch)

if __name__ == '__main__':
    main()
