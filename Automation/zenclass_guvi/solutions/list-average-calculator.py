import sys

data = sys.stdin.read().split()
if not data:
    print(0)
else:
    values = [float(x) for x in data]
    print(sum(values) / len(values))
