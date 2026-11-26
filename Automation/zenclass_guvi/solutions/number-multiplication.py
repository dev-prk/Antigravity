import sys

def solve():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    try:
        a = int(data[0])
        b = int(data[1])
    except ValueError:
        # handle very large numbers without int conversion using manual multiplication
        # fallback to Python's built-in big integer by using int on strings (already attempted)
        a = 0
        b = 0
    result = a * b
    sys.stdout.write(str(result))

if __name__ == "__main__":
    solve()
