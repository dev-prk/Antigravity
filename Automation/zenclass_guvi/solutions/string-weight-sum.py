import sys

def main():
    s = sys.stdin.readline()
    if s.endswith('\n'):
        s = s[:-1]
    total = sum(ord(c) for c in s)
    print(total)

if __name__ == "__main__":
    main()
