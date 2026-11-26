import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    
    # Extract elements at even indices (0-based)
    even_vals = [arr[i] for i in range(0, n, 2)]
    even_vals.sort()
    
    # Put them back
    idx = 0
    for i in range(0, n, 2):
        arr[i] = even_vals[idx]
        idx += 1
    
    sys.stdout.write(" ".join(map(str, arr)))

if __name__ == "__main__":
    solve()
