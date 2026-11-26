import sys

data = sys.stdin.read().split()
if not data:
    sys.exit(0)

s = data[0]

if len(data) > 1:
    try:
        k = int(data[1])
    except ValueError:
        k = 0
else:
    k = 0

n = len(s)
if n == 0:
    print("")
else:
    k %= n
    sys.stdout.write(s[k:] + s[:k] + "\n")
