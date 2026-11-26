import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    R = int(next(it))
    C = int(next(it))
    grid = []
    for _ in range(R):
        row = [int(next(it)) for _ in range(C)]
        grid.append(row)

    if grid[0][0] == 1 or grid[R-1][C-1] == 1:
        print(-1)
        return

    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    dist = [[-1] * C for _ in range(R)]
    q = deque()
    dist[0][0] = 0
    q.append((0, 0))

    while q:
        r, c = q.popleft()
        if r == R-1 and c == C-1:
            print(dist[r][c])
            return
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                if grid[nr][nc] == 0 and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))

    print(-1)

if __name__ == "__main__":
    main()
