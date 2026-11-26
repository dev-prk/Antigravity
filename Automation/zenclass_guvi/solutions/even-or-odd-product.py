import sys

def solve() -> None:
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    # Check the next n numbers (or all available if fewer)
    for i in range(1, min(len(data), n + 1)):
        if int(data[i]) % 2 == 0:
            print("even")
            return
    print("odd")

if __name__ == "__main__":
    solve()
