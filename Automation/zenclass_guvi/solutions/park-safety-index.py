import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    R = int(data[idx])
    C = int(data[idx+1])
    idx += 2
    
    gates = []
    for _ in range(3):
        r = int(data[idx])
        c = int(data[idx+1])
        gates.append((r-1, c-1))
        idx += 2
    
    cage_r = int(data[idx]) - 1
    cage_c = int(data[idx+1]) - 1
    idx += 2
    
    grid = []
    for r in range(R):
        row = []
        for c in range(C):
            row.append(data[idx])
            idx += 1
        grid.append(row)
    
    total_grasslands = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 'G':
                total_grasslands += 1
    
    t_rex_dist = [[-1]*C for _ in range(R)]
    q = deque()
    t_rex_dist[cage_r][cage_c] = 0
    q.append((cage_r, cage_c))
    
    while q:
        r, c = q.popleft()
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                if t_rex_dist[nr][nc] == -1:
                    if grid[nr][nc] in ['G', 'M']:
                        t_rex_dist[nr][nc] = t_rex_dist[r][c] + 1
                        q.append((nr, nc))
    
    person_dist = [[-1]*C for _ in range(R)]
    gate_dist = [[-1]*C for _ in range(R)]
    
    for gate_r, gate_c in gates:
        if grid[gate_r][gate_c] == 'G':
            q = deque()
            q.append((gate_r, gate_c))
            gate_dist[gate_r][gate_c] = 0
            
            while q:
                r, c = q.popleft()
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < R and 0 <= nc < C:
                        if gate_dist[nr][nc] == -1 and grid[nr][nc] == 'G':
                            gate_dist[nr][nc] = gate_dist[r][c] + 1
                            q.append((nr, nc))
    
    q = deque()
    for r in range(R):
        for c in range(C):
            if gate_dist[r][c] >= 0:
                person_dist[r][c] = gate_dist[r][c]
                q.append((r, c))
    
    while q:
        r, c = q.popleft()
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                if person_dist[nr][nc] == -1 and grid[nr][nc] == 'G':
                    person_dist[nr][nc] = person_dist[r][c] + 1
                    q.append((nr, nc))
    
    safe_count = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 'G':
                if t_rex_dist[r][c] == -1:
                    safe_count += 1
                else:
                    gate_times = []
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 'G' and gate_dist[nr][nc] >= 0:
                            gate_times.append(gate_dist[nr][nc] + 1)
                    
                    if not gate_times:
                        min_gate_time = float('inf')
                    else:
                        min_gate_time = min(gate_times)
                    
                    t_rex_chase_time = t_rex_dist[r][c] + 1
                    
                    if min_gate_time < t_rex_chase_time:
                        safe_count += 1
    
    if total_grasslands == 0:
        print("0.00")
    else:
        safety_index = (safe_count * 100) / total_grasslands
        print("{:.2f}".format(safety_index))

if __name__ == "__main__":
    main()
