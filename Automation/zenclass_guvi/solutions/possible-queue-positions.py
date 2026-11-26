import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n, a, b = map(int, data[:3])
    ans = min(n - a, b + 1)
    print(ans)

if __name__ == "__main__":
    main()
