import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    idx = 0
    R = int(data[idx])
    idx += 1
    C = int(data[idx])
    idx += 1
    
    U = int(data[idx])
    idx += 1
    
    grid = [[0] * C for _ in range(R)]
    
    for _ in range(U):
        r1 = int(data[idx]) - 1
        idx += 1
        c1 = int(data[idx]) - 1
        idx += 1
        r2 = int(data[idx]) - 1
        idx += 1
        c2 = int(data[idx]) - 1
        idx += 1
        value = int(data[idx])
        idx += 1
        
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                grid[r][c] += value
    
    total = 0
    for row in grid:
        for val in row:
            total += val
    
    print(f"Total number of products: {total}")

if __name__ == "__main__":
    main()
