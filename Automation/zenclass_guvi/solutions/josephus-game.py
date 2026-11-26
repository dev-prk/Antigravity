import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    idx = 0
    t = int(data[idx])
    idx += 1
    out = []
    for _ in range(t):
        n = int(data[idx])
        k = int(data[idx + 1])
        idx += 2
        
        positions = list(range(1, n + 1))
        
        while len(positions) >= k:
            num_survive = len(positions) // k
            new_positions = []
            for i in range(num_survive):
                new_positions.append(positions[i * k + k - 1])
            positions = new_positions
        
        out.append(str(min(positions)) if positions else "-1")
    
    print("\n".join(out))

solve()
