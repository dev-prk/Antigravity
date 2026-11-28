import sys

def solve():
    data = sys.stdin.read().splitlines()
    if not data:
        print(-1)
        return
    
    n = int(data[0].strip())
    queue = []
    
    for i in range(1, n + 1):
        line = data[i].strip()
        if line.startswith("ENQUEUE"):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    x = int(parts[1])
                    queue.append(x)
                except ValueError:
                    pass
        elif line == "DEQUEUE":
            if queue:
                queue.pop(0)
    
    if not queue:
        print(-1)
    else:
        print(" ".join(map(str, queue)), end=' ')

if __name__ == "__main__":
    solve()
