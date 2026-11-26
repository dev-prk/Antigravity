import sys

s = sys.stdin.readline().rstrip('\n')
if s.endswith('\r'):
    s = s[:-1]

letters = []
total = 0

for ch in s:
    if '0' <= ch <= '9':
        total += ord(ch) - ord('0')
    else:
        letters.append(ch)

print(''.join(letters) + str(total))
