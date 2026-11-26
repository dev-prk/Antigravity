import sys
import math

class SegmentTree:
    def __init__(self, data, func, default):
        self.n = len(data)
        self.func = func
        self.default = default
        self.size = 1
        while self.size < self.n:
            self.size *= 2
        self.tree = [self.default] * (2 * self.size)
        # Fill leaves
        for i in range(self.n):
            self.tree[self.size + i] = data[i]
        # Build tree
        for i in range(self.size - 1, 0, -1):
            self.tree[i] = self.func(self.tree[2 * i], self.tree[2 * i + 1])
    
    def query(self, l, r):
        # Query range [l, r] inclusive, 0-indexed
        l += self.size
        r += self.size
        res_left = self.default
        res_right = self.default
        while l <= r:
            if l % 2 == 1:
                res_left = self.func(res_left, self.tree[l])
                l += 1
            if r % 2 == 0:
                res_right = self.func(self.tree[r], res_right)
                r -= 1
            l //= 2
            r //= 2
        return self.func(res_left, res_right)

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    if N == 0:
        Q = int(data[idx])
        idx += 1
        for _ in range(Q):
            idx += 2  # skip L and R
            print(0)
        return
    
    arr = list(map(int, data[idx:idx+N]))
    idx += N
    
    Q = int(data[idx])
    idx += 1
    
    # Build segment trees (1-indexed for problem)
    seg_max = SegmentTree(arr, max, float('-inf'))
    seg_min = SegmentTree(arr, min, float('inf'))
    
    results = []
    for _ in range(Q):
        L = int(data[idx])
        R = int(data[idx+1])
        idx += 2
        
        # Convert to 0-indexed
        l = L - 1
        r = R - 1
        
        if l > r:
            l, r = r, l
        
        max_val = seg_max.query(l, r)
        min_val = seg_min.query(l, r)
        results.append(str(int(max_val - min_val)))
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
