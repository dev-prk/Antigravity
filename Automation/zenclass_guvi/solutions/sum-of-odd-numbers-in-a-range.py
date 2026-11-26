import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    L, R = int(data[0]), int(data[1])
    
    if L > R:
        print(-1)
        return
    
    if L % 2 == 0:
        first_odd = L + 1
    else:
        first_odd = L
    
    if R % 2 == 0:
        last_odd = R - 1
    else:
        last_odd = R
    
    if first_odd > last_odd:
        print(-1)
        return
    
    n = ((last_odd - first_odd) // 2) + 1
    total = n * (first_odd + last_odd) // 2
    print(total)

if __name__ == "__main__":
    solve()
