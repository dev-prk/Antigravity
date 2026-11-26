import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))
    # stable sort by descending number of set bits
    nums.sort(key=lambda x: -bin(x).count('1'))
    sys.stdout.write(' '.join(map(str, nums)))

if __name__ == "__main__":
    solve()
