import sys

def main():
    s = sys.stdin.readline()
    if s.endswith('\n'):
        s = s[:-1]
    print(s[::-1])

if __name__ == "__main__":
    main()
