import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    # Read the next N values (the Q values for initial state)
    Q_values = list(map(int, data[idx:idx+N]))
    idx += N
    
    E = int(data[idx])
    idx += 1
    
    # Initialize arrays for segment tree
    # Using difference array approach for range updates
    size = 4 * N
    tree_sum = [0] * size
    tree_lazy = [0] * size
    
    def build(node, start, end):
        if start == end:
            tree_sum[node] = Q_values[start - 1]  # 1-indexed to 0-indexed
        else:
            mid = (start + end) // 2
            build(2*node, start, mid)
            build(2*node+1, mid+1, end)
            tree_sum[node] = tree_sum[2*node] + tree_sum[2*node+1]
    
    def push(node, start, end):
        if tree_lazy[node] != 0:
            tree_sum[node] += tree_lazy[node] * (end - start + 1)
            if start != end:
                tree_lazy[2*node] += tree_lazy[node]
                tree_lazy[2*node+1] += tree_lazy[node]
            tree_lazy[node] = 0
    
    def update_range(node, start, end, l, r, val):
        push(node, start, end)
        if start > r or end < l:
            return
        if l <= start and end <= r:
            tree_lazy[node] += val
            push(node, start, end)
            return
        mid = (start + end) // 2
        update_range(2*node, start, mid, l, r, val)
        update_range(2*node+1, mid+1, end, l, r, val)
        tree_sum[node] = tree_sum[2*node] + tree_sum[2*node+1]
    
    def query_range(node, start, end, l, r):
        if start > r or end < l:
            return 0
        push(node, start, end)
        if l <= start and end <= r:
            return tree_sum[node]
        mid = (start + end) // 2
        left_sum = query_range(2*node, start, mid, l, r)
        right_sum = query_range(2*node+1, mid+1, end, l, r)
        return left_sum + right_sum
    
    build(1, 1, N)
    
    output = []
    for _ in range(E):
        op = int(data[idx])
        idx += 1
        if op == 1:
            x = int(data[idx])
            idx += 1
            y = int(data[idx])
            idx += 1
            Q = int(data[idx])
            idx += 1
            update_range(1, 1, N, x, y, Q)
        else:
            L = int(data[idx])
            idx += 1
            R = int(data[idx])
            idx += 1
            result = query_range(1, 1, N, L, R)
            output.append(str(result))
    
    print('\n'.join(output))

if __name__ == "__main__":
    main()
