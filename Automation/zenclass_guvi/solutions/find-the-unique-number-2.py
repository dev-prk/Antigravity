import sys

def solve() -> None:
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1+n]))
    freq = {}
    for x in nums:
        freq[x] = freq.get(x, 0) + 1
    for x, cnt in freq.items():
        if cnt == 1:
            print(x)
            return

if __name__ == "__main__":
    solve()
