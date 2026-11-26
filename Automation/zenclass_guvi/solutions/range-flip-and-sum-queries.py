import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    arr = [0] * (n + 2)
    for i in range(1, n + 1):
        arr[i] = int(data[idx])
        idx += 1
    
    q = int(data[idx])
    idx += 1
    
    size = 4 * (n + 2)
    tree = [0] * size
    lazy = [0] * size
    
    def build(node, start, end):
        if start == end:
            tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            build(2 * node, start, mid)
            build(2 * node + 1, mid + 1, end)
            tree[node] = tree[2 * node] + tree[2 * node + 1]
    
    build(1, 1, n)
    
    def push(node, start, end):
        if lazy[node] != 0:
            tree[node] = (end - start + 1) - tree[node]
            if start != end:
                lazy[2 * node] ^= 1
                lazy[2 * node + 1] ^= 1
            lazy[node] = 0
    
    def update_range(node, start, end, l, r):
        push(node, start, end)
        if start > r or end < l:
            return
        if l <= start and end <= r:
            lazy[node] ^= 1
            push(node, start, end)
            return
        mid = (start + end) // 2
        update_range(2 * node, start, mid, l, r)
        update_range(2 * node + 1, mid + 1, end, l, r)
        tree[node] = tree[2 * node] + tree[2 * node + 1]
    
    def query_sum(node, start, end, l, r):
        push(node, start, end)
        if start > r or end < l:
            return 0
        if l <= start and end <= r:
            return tree[node]
        mid = (start + end) // 2
        left_sum = query_sum(2 * node, start, mid, l, r)
        right_sum = query_sum(2 * node + 1, mid + 1, end, l, r)
        return left_sum + right_sum
    
    output = []
    for _ in range(q):
        op = int(data[idx])
        x = int(data[idx + 1])
        y = int(data[idx + 2])
        idx += 3
        
        if op == 1:
            update_range(1, 1, n, x, y)
        else:
            result = query_sum(1, 1, n, x, y)
            output.append(str(result))
    
    print('\n'.join(output))

if __name__ == "__main__":
    main()
