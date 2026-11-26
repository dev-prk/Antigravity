import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    P = list(map(int, data[idx:idx+N]))
    idx += N
    
    Q = int(data[idx])
    idx += 1
    
    queries = []
    for _ in range(Q):
        t = int(data[idx])
        x = int(data[idx+1])
        y = int(data[idx+2])
        queries.append((t, x, y))
        idx += 3
    
    # Build segment tree for range minimum query
    size = 1
    while size < N:
        size *= 2
    seg = [float('inf')] * (2 * size)
    
    # Initialize leaves
    for i in range(N):
        seg[size + i] = P[i]
    for i in range(size - 1, 0, -1):
        seg[i] = min(seg[2*i], seg[2*i+1])
    
    def update(pos, val):
        p = size + pos - 1  # 1-based to 0-based index in array
        seg[p] = val
        p //= 2
        while p >= 1:
            seg[p] = min(seg[2*p], seg[2*p+1])
            p //= 2
    
    def query(l, r):
        # l, r are 1-based, query [l, r]
        l0 = l - 1
        r0 = r - 1
        l += size - 1
        r += size - 1
        res = float('inf')
        while l <= r:
            if l % 2 == 1:
                res = min(res, seg[l])
                l += 1
            if r % 2 == 0:
                res = min(res, seg[r])
                r -= 1
            l //= 2
            r //= 2
        return res
    
    output = []
    for t, x, y in queries:
        if t == 1:
            # Batman increases power of batmobile x by y
            pos = x - 1
            update(pos, P[pos] + y)
            P[pos] += y
        elif t == 2:
            # Bane attacks batmobile x with power y
            pos = x - 1
            P[pos] -= y
            update(pos, P[pos])
        else:
            # Query if any batmobile from x to y has power 0
            min_val = query(x, y)
            if min_val <= 0:
                output.append("escape")
            else:
                output.append("stay and fight")
    
    for line in output:
        print(line)

if __name__ == "__main__":
    main()
