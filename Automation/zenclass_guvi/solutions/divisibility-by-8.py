import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        n = int(data[0])
    except:
        # handle very large numbers without converting to int by using last three digits
        s = data[0].lstrip('-')
        if len(s) > 3:
            s = s[-3:]
        n = int(s)
        if data[0].startswith('-'):
            n = -n
    result = 1 if n % 8 == 0 else 0
    sys.stdout.write(str(result))

if __name__ == "__main__":
    solve()
