import sys

for line in sys.stdin:
    day = line.strip().lower()
    if day in ('saturday', 'sunday'):
        print('yes')
    else:
        print('no')
