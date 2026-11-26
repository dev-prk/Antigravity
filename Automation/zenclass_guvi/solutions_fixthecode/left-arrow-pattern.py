a = int(input())

# Top part: diagonal lines (excluding the center line)
for i in range(a - 1):
    print(' ' * i + '*')

# Center line: solid line of a stars
print('*' * a)

# Bottom part: diagonal lines in reverse
for i in range(a - 2, -1, -1):
    print(' ' * i + '*')
