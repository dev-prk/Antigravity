import sys

def solve() -> None:
    data = sys.stdin.read()
    if not data:
        return
    s = data.strip()
    n = len(s)
    if n == 0:
        sys.stdout.write("0")
        return

    vowels = set('aeiouAEIOU')
    max_len = 0
    cur_len = 1

    for i in range(1, n):
        if (s[i] in vowels) != (s[i - 1] in vowels):
            cur_len += 1
        else:
            if cur_len > max_len:
                max_len = cur_len
            cur_len = 1

    if cur_len > max_len:
        max_len = cur_len

    if max_len < 2:
        max_len = 0
    sys.stdout.write(str(max_len))

if __name__ == "__main__":
    solve()
