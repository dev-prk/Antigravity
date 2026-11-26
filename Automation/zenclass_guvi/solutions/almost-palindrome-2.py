import sys

def solve():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    s = data[0].strip()  # or rstrip?
    n = len(s)
    mismatches = 0
    for i in range(n // 2):
        if s[i] != s[n - 1 - i]:
            mismatches += 1
            if mismatches > 1:
                print('no')
                return
    print('yes')

if __name__ == '__main__':
    solve()
