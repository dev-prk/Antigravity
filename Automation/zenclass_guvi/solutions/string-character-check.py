import sys

s = sys.stdin.readline()
if s.endswith('\n'):
    s = s[:-1]
if s.endswith('\r'):
    s = s[:-1]

ok = True
for ch in s:
    if ch != 'a' and ch != 'b':
        ok = False
        break

sys.stdout.write('yes' if ok else 'no')
