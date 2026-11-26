import sys

def solve() -> None:
    s = sys.stdin.read()
    if not s:
        print(-1)
        return
    # Remove possible trailing newlines but keep other spaces
    s = s.rstrip('\n')
    vowels = set('aeiouAEIOU')
    res = []
    cnt = 0
    for ch in s:
        if ch == ' ':
            res.append(ch)
        elif ch.isalpha() and ch not in vowels:
            res.append(ch)
            cnt += 1
        # else: ignore (vowels, digits, punctuation, etc.)
    if cnt == 0:
        print(-1)
    else:
        print(''.join(res))

if __name__ == "__main__":
    solve()
