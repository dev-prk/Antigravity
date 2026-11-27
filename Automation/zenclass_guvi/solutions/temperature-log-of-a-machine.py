n = int(input())
readings = [int(input()) for _ in range(n)]
limit = int(input())
print(max(readings))
print(sum(1 for r in readings if r > limit))
