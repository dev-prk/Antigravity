import sys
import heapq

def main():
    data = sys.stdin.read().split()
    if not data:
        print(-1)
        return
    
    idx = 0
    N = int(data[idx])
    M = int(data[idx+1])
    idx += 2
    
    grid = []
    for _ in range(N):
        row = list(map(int, data[idx:idx+M]))
        grid.append(row)
        idx += M
    
    source_str = data[idx]
    dest_str = data[idx+1]
    idx += 2
    
    src_row, src_col = map(int, source_str.split(','))
    dest_row, dest_col = map(int, dest_str.split(','))
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    INF = 10**18
    dist = [[INF] * M for _ in range(N)]
    dist[src_row][src_col] = 0
    
    heap = []
    heapq.heappush(heap, (0, src_row, src_col))
    
    while heap:
        time, r, c = heapq.heappop(heap)
        
        if r == dest_row and c == dest_col:
            print(time)
            return
        
        if time > dist[r][c]:
            continue
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < M:
                new_time = time + grid[nr][nc]
                if new_time < dist[nr][nc]:
                    dist[nr][nc] = new_time
                    heapq.heappush(heap, (new_time, nr, nc))
    
    print(-1)

if __name__ == "__main__":
    main()
