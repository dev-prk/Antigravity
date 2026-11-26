import sys
s = sys.stdin.readline().rstrip('\n')
result = ''.join(c for c in s if c.isalnum() or c.isspace())
if result == s:
    print(-1)
else:
    print(result)
