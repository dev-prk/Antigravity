import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    s = data[0]
    n = len(s)
    # prefix sum of digit values
    pref = [0] * (n + 1)
    for i, ch in enumerate(s, 1):
        pref[i] = pref[i - 1] + (ord(ch) - 48)  # assuming digit characters

    ans = 0
    # try lengths from largest even down to 2
    for length in range(n if n % 2 == 0 else n - 1, 1, -2):
        half = length // 2
        found = False
        for i in range(0, n - length + 1):
            mid = i + half
            left_sum = pref[mid] - pref[i]
            right_sum = pref[i + length] - pref[mid]
            if left_sum == right_sum:
                ans = length
                found = True
                break
        if found:
            break

    print(ans)

if __name__ == "__main__":
    solve()
