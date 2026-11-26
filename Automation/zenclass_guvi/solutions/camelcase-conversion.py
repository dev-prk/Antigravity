import sys

s = sys.stdin.read()
parts = s.split()
if parts:
    sys.stdout.write("".join(w[0].upper() + w[1:] for w in parts))
else:
    sys.stdout.write("")
