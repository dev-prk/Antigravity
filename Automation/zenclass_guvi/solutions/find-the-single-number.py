import sys

data = sys.stdin.buffer.read().split()
if not data:
    sys.exit(0)

n = int(data[0])
ans = 0

for x in data[1:1 + n]:
    ans ^= int(x)

print(ans)
