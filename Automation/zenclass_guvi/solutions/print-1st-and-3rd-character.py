import sys

s = sys.stdin.readline().rstrip('\n\r')
if len(s) >= 3:
    sys.stdout.write(s[0] + s[2] + '\n')
elif len(s) >= 1:
    sys.stdout.write(s[0] + '\n')
else:
    sys.stdout.write('\n')
