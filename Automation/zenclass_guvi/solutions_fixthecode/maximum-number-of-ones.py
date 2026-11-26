n = int(input())
l = [int(x) for x in input().split()]
z = int(input())

# Sort by number of 1s in binary (descending), then by value (descending) for tie-breaker
l.sort(key=lambda x: (bin(x).count('1'), x), reverse=True)

print(*l[:z])
