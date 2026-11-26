import sys

def solve() -> None:
    s = sys.stdin.read().rstrip('\n')
    uppers = sorted(c for c in s if c.isupper())
    lowers = sorted(c for c in s if c.islower())
    res = []
    i_u = i_l = 0
    for ch in s:
        if ch.isupper():
            res.append(uppers[i_u])
            i_u += 1
        elif ch.islower():
            res.append(lowers[i_l])
            i_l += 1
        else:
            res.append(ch)
    sys.stdout.write(''.join(res))

if __name__ == "__main__":
    solve()
