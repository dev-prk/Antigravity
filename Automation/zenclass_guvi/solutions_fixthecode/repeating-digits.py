a = input().strip()
b = set(a)
if len(b) < len(a):
    print("yes", end='')
else:
    print("no", end='')
