import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    idx = 0
    t = int(data[idx])
    idx += 1
    results = []
    for _ in range(t):
        n = int(data[idx])
        idx += 1
        if n == 0:
            results.append(0)
            continue
        heights = list(map(int, data[idx:idx+n]))
        idx += n
        
        count = 0
        max_height = 0
        for h in reversed(heights):
            if h > max_height:
                count += 1
                max_height = h
        
        results.append(count)
    
    for res in results:
        print(res)

if __name__ == "__main__":
    solve()
