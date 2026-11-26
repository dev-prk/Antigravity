import sys

s = sys.stdin.read().rstrip('\n')
result = len(s.replace(' ', ''))
print(result)
