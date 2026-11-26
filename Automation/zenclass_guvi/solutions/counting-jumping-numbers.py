import sys

def is_jumping(x: int) -> bool:
    s = str(x)
    for i in range(len(s) - 1):
        if abs(int(s[i]) - int(s[i + 1])) != 1:
            return False
    return True

def main() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    N = int(data[0])
    cnt = 0
    for i in range(N + 1):
        if is_jumping(i):
            cnt += 1
    print(cnt)

if __name__ == "__main__":
    main()
