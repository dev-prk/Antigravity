import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    arr = list(map(int, data[idx:idx+N]))
    idx += N
    
    Q = int(data[idx])
    idx += 1
    
    # Convert: 0 -> 1 (fake), 1 -> -1 (real)
    # So sum > 0 means more fake, sum < 0 means more real
    converted = [1 if x == 0 else -1 for x in arr]
    
    # Build segment tree
    size = 1
    while size < N:
        size *= 2
    
    tree = [0] * (2 * size)
    
    for i in range(N):
        tree[size + i] = converted[i]
    
    for i in range(size - 1, 0, -1):
        tree[i] = tree[2 * i] + tree[2 * i + 1]
    
    def update(pos, val):
        p = size + pos
        tree[p] = val
        p //= 2
        while p >= 1:
            tree[p] = tree[2 * p] + tree[2 * p + 1]
            p //= 2
    
    def query(l, r):
        l += size
        r += size
        res = 0
        while l <= r:
            if l % 2 == 1:
                res += tree[l]
                l += 1
            if r % 2 == 0:
                res += tree[r]
                r -= 1
            l //= 2
            r //= 2
        return res
    
    output = []
    
    for _ in range(Q):
        t = int(data[idx])
        idx += 1
        
        if t == 1:
            x = int(data[idx])
            idx += 1
            pos = x - 1
            # Toggle the value
            if arr[pos] == 0:
                arr[pos] = 1
                update(pos, -1)
            else:
                arr[pos] = 0
                update(pos, 1)
        else:
            x = int(data[idx])
            y = int(data[idx + 1])
            idx += 2
            l = x - 1
            r = y - 1
            s = query(l, r)
            if s > 0:
                output.append("Dissatisfied")
            elif s < 0:
                output.append("Satisfied")
            else:
                output.append("Neutral")
    
    print('\n'.join(output))

if __name__ == "__main__":
    main()
