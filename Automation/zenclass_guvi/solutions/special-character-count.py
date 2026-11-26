import sys

def main():
    s = sys.stdin.read()
    cnt = sum(1 for ch in s if not ch.isalnum() and not ch.isspace())
    print(-1 if cnt == 0 else cnt)

if __name__ == "__main__":
    main()
