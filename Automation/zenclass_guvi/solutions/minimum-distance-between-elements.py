import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    
    arr = list(map(int, data[1:1+n]))
    u = int(data[1+n])
    v = int(data[2+n])
    
    min_dist = float('inf')
    last_u = -1
    last_v = -1
    
    for i in range(n):
        if arr[i] == u:
            last_u = i
            if last_v != -1:
                min_dist = min(min_dist, last_u - last_v)
        if arr[i] == v:
            last_v = i
            if last_u != -1:
                min_dist = min(min_dist, last_v - last_u)
    
    if min_dist == float('inf'):
        print(-1)
    else:
        print(min_dist)

if __name__ == "__main__":
    main()
