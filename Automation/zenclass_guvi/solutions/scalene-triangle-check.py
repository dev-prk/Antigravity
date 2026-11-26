import sys

data = sys.stdin.buffer.read().split()
if len(data) < 3:
    print("no")
else:
    a, b, c = map(int, data[:3])
    if a <= 0 or b <= 0 or c <= 0 or a == b or b == c or a == c:
        print("no")
    else:
        x, y, z = sorted((a, b, c))
        print("yes" if x + y > z else "no")
