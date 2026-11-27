n = int(input())
total_distance = 0
total_walks = 0
for _ in range(n):
    walks = list(map(int, input().split()))
    total_distance += sum(walks)
    total_walks += len(walks)
print(total_distance)
print(total_walks)
