import sys, collections

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    if n <= 0 or m <= 0:
        print(0)
        return
    vals = list(map(int, data[2:2 + n * m]))
    grid = [vals[i * m:(i + 1) * m] for i in range(n)]

    q = collections.deque()
    fresh = 0
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 2:
                q.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1

    if fresh == 0:
        print(0)
        return

    minutes = -1
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        minutes += 1
        for _ in range(len(q)):
            x, y = q.popleft()
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] == 1:
                    grid[nx][ny] = 2
                    fresh -= 1
                    q.append((nx, ny))

    print(minutes if fresh == 0 else -1)

if __name__ == "__main__":
    solve()
