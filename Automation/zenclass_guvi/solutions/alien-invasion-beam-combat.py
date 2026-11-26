import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    X = int(data[idx+1])
    Y = int(data[idx+2])
    idx += 3
    
    powers = [0] * (N + 1)
    for i in range(1, N + 1):
        powers[i] = int(data[idx])
        idx += 1
    
    Q = int(data[idx])
    idx += 1
    
    # segment tree for defeated count
    size = 1
    while size < N:
        size *= 2
    defeated_tree = [0] * (2 * size)
    
    def update_defeated(pos, val):
        pos += size - 1
        defeated_tree[pos] = val
        pos //= 2
        while pos >= 1:
            defeated_tree[pos] = defeated_tree[2*pos] + defeated_tree[2*pos+1]
            pos //= 2
    
    def query_defeated(l, r):
        l += size - 1
        r += size - 1
        res = 0
        while l <= r:
            if l % 2 == 1:
                res += defeated_tree[l]
                l += 1
            if r % 2 == 0:
                res += defeated_tree[r]
                r -= 1
            l //= 2
            r //= 2
        return res
    
    # initialize defeated tree
    for i in range(1, N + 1):
        if powers[i] == 0:
            update_defeated(i, 1)
    
    output = []
    
    for _ in range(Q):
        event_type = int(data[idx])
        x = int(data[idx+1])
        y_str = data[idx+2]
        idx += 3
        
        if event_type == 1:
            # shoot event
            if y_str == 'A':
                damage = X
            else:
                damage = Y
            
            if powers[x] > 0:
                powers[x] -= damage
                if powers[x] <= 0:
                    update_defeated(x, 1)
        else:
            # query event
            res = query_defeated(x, int(y_str))
            output.append(str(res))
    
    print('\n'.join(output))

if __name__ == "__main__":
    main()
