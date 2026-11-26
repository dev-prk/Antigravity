import sys
from collections import deque

def main() -> None:
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    total = n * m
    # read grid values
    grid = [0] * total
    for i in range(total):
        grid[i] = int(next(it))
    # helper to access cell (r,c)
    def cell(r, c):
        return grid[r * m + c]
    # start or end blocked?
    if cell(0, 0) == 0 or cell(n - 1, m - 1) == 0:
        print(0)
        return
    # BFS
    visited = [False] * total
    q = deque()
    q.append((0, 0))
    visited[0] = True
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        r, c = q.popleft()
        if r == n - 1 and c == m - 1:
            print(1)
            return
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                idx = nr * m + nc
                if not visited[idx] and cell(nr, nc) == 1:
                    visited[idx] = True
                    q.append((nr, nc))
    print(0)

if __name__ == "__main__":
    main()
