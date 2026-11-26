t = int(input())
rem = 3
cycle_start = 1

while t >= cycle_start + rem:
    cycle_start += rem
    rem *= 2

print(cycle_start + rem - t)
