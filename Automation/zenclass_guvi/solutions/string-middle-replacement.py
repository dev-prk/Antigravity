import sys

def solve():
    s = sys.stdin.readline().strip()
    n = len(s)
    if n == 0:
        print("")
        return
    if n % 2 == 1:
        mid = n // 2
        result = s[:mid] + "*" + s[mid + 1:]
    else:
        mid_right = n // 2
        mid_left = mid_right - 1
        result = s[:mid_left] + "**" + s[mid_right + 1:]
    print(result)

if __name__ == "__main__":
    solve()
