import sys

def solve() -> None:
    data = sys.stdin.read()
    if not data:
        return
    word = data.strip()
    # According to problem, word contains only letters and no spaces, length >= 1
    length = len(word)
    first = word[0]
    last = word[-1]
    reversed_word = word[::-1]
    upper_word = word.upper()
    out = [
        str(length),
        first,
        last,
        reversed_word,
        upper_word
    ]
    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    solve()
