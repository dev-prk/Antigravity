import sys

def solve() -> None:
    data = sys.stdin.read().strip()
    if not data:
        print(0)
        return

    # count digits 0-9
    counts = [0] * 10
    for ch in data:
        if ch.isdigit():
            counts[int(ch)] += 1

    # build the largest number by putting digits in descending order
    parts = []
    for d in range(9, -1, -1):
        if counts[d]:
            parts.append(str(d) * counts[d])

    ans = ''.join(parts)

    # if the largest digit is 0, the number is zero
    if ans[0] == '0':
        print(0)
    else:
        print(ans)

if __name__ == "__main__":
    solve()
