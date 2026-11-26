import sys

def solve() -> None:
    s = sys.stdin.read().strip()
    if not s:
        return
    res = []
    i = 0
    n = len(s)
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        cnt = j - i
        res.append(s[i] + str(cnt))
        i = j
    sys.stdout.write(''.join(res))

if __name__ == "__main__":
    solve()
