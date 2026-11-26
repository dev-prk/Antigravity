import sys

def solve():
    data = sys.stdin.read().strip()
    if not data:
        return
    # Remove leading sign if present
    if data[0] in '+-':
        data = data[1:]
    if not data:
        return
    # First and last digit
    first = int(data[0])
    last = int(data[-1])
    print(first + last)

if __name__ == '__main__':
    solve()
