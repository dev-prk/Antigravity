import sys

def solve() -> None:
    line = sys.stdin.readline()
    if not line:
        return
    line = line.strip()
    if not line:
        return
    n = int(line.split()[0])
    print("yes" if n % 11 == 0 else "no")

if __name__ == "__main__":
    solve()
