import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if n < 3:
        print(0)
        return
    
    # Coordinate compression
    sorted_unique = sorted(arr)
    rank = {val: i+1 for i, val in enumerate(sorted_unique)}
    m = len(rank)
    
    # Fenwick Tree implementation
    class FenwickTree:
        def __init__(self, size):
            self.n = size
            self.tree = [0] * (self.n + 1)
        
        def update(self, idx, delta):
            while idx <= self.n:
                self.tree[idx] += delta
                idx += idx & (-idx)
        
        def query(self, idx):
            s = 0
            while idx > 0:
                s += self.tree[idx]
                idx -= idx & (-idx)
            return s
    
    # Step 1: Calculate L[i] - count of elements greater than arr[i] to the left
    ft_left = FenwickTree(m)
    L = [0] * n
    
    for i in range(n):
        r = rank[arr[i]]
        # Count elements already in BIT with rank > r
        L[i] = ft_left.query(m) - ft_left.query(r)
        ft_left.update(r, 1)
    
    # Step 2: Calculate R[i] - count of elements smaller than arr[i] to the right
    ft_right = FenwickTree(m)
    R = [0] * n
    
    for i in range(n-1, -1, -1):
        r = rank[arr[i]]
        # Count elements already in BIT with rank < r
        R[i] = ft_right.query(r - 1)
        ft_right.update(r, 1)
    
    # Step 3: Sum L[i] * R[i] for all i
    result = sum(L[i] * R[i] for i in range(n))
    print(result)

if __name__ == "__main__":
    main()
