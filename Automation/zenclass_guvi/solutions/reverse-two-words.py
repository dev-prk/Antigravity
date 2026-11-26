import sys

def solve() -> None:
    data = sys.stdin.read()
    # Remove trailing newlines but keep possible leading spaces for splitting
    words = data.split()
    if not words:
        return
    reversed_words = words[::-1]
    sys.stdout.write(' '.join(reversed_words))

if __name__ == "__main__":
    solve()
