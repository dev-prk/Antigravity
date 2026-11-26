import sys

def solve() -> None:
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    k = int(data[2])
    # read exactly n numbers, ignoring any extra whitespace
    nums = list(map(int, data[3:3 + n]))
    # collect numbers strictly between m and k
    between = [str(x) for x in nums if m < x < k]
    if not between:
        print(-1)
    else:
        print(' '.join(between))

if __name__ == "__main__":
    solve()
