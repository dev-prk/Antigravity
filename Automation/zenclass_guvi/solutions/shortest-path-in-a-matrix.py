import sys, heapq

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    try:
        n = int(next(it))
        m = int(next(it))
    except StopIteration:
        return

    # handle possible zero dimensions
    if n <= 0 or m <= 0:
        print(-1)
        return

    grid = [[0] * m for _ in range(n)]
    start = end = None

    for i in range(n):
        for j in range(m):
            try:
                token = next(it)
            except StopIteration:
                token = ''
            if token == 'A':
                start = (i, j)
                grid[i][j] = 0
            elif token == 'B':
                end = (i, j)
                grid[i][j] = 0
            else:
                # token may be numeric (including negative)
                try:
                    grid[i][j] = int(token)
                except:
                    # in case of malformed token, treat as 0
                    grid[i][j] = 0

    if start is None or end is None:
        print(-1)
        return

    INF = 10**18
    dist = [[INF] * m for _ in range(n)]
    sr, sc = start
    dist[sr][sc] = 0
    heap = [(0, sr, sc)]
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]

    while heap:
        d, r, c = heapq.heappop(heap)
        if d != dist[r][c]:
            continue
        if (r, c) == end:
            break
        nd = d
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                w = grid[nr][nc]
                ndist = d + w
                if ndist < dist[nr][nc]:
                    dist[nr][nc] = ndist
                    heapq.heappush(heap, (ndist, nr, nc))

    er, ec = end
    ans = dist[er][ec]
    print(ans if ans != INF else -1)

if __name__ == "__main__":
    solve()
