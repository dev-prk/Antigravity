import sys

def count_set_bits(n):
    count = 0
    while n > 0:
        n = n & (n - 1)
        count += 1
    return count

line = sys.stdin.readline().strip()
x = int(line.split('=')[1])
print(count_set_bits(x))
