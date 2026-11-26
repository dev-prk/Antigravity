import sys

def solve() -> None:
    data = sys.stdin.read().splitlines()
    if not data:
        return
    s = data[0].rstrip('\n')
    n = len(s)
    if n == 0:
        return
    for i in range(n):
        if i == 0:
            line = s
        elif i == n - 1:
            line = s[::-1]
        else:
            line = s[i] + ' ' * (n - 2) + s[n - 1 - i]
        sys.stdout.write(line)
        if i != n - 1:
            sys.stdout.write('\n')

if __name__ == "__main__":
    solve()
