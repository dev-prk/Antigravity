import sys
print(sum(1 for c in sys.stdin.read() if c not in ' \n\r'))
