import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    X = int(data[1])
    q = int(data[2])
    
    if n == 0 or q == 0:
        for _ in range(q):
            print(X)
        return
    
    idx = 3
    queries = []
    for _ in range(q):
        tp = int(data[idx])
        x = int(data[idx + 1])
        y = int(data[idx + 2])
        queries.append((tp, x, y))
        idx += 3
    
    heights = [X] * (n + 2)
    for tp, x, y in queries:
        if tp == 1:
            if 1 <= x <= n:
                heights[x] -= y
        else:
            max_val = 0
            for i in range(min(x, y), max(x, y) + 1):
                if 1 <= i <= n and heights[i] > max_val:
                    max_val = heights[i]
            print(max_val)

if __name__ == "__main__":
    main()
