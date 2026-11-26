import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    T = int(data[idx])
    idx += 1
    
    results = []
    
    for _ in range(T):
        N = int(data[idx])
        idx += 1
        
        batch_a = list(map(int, data[idx:idx+N]))
        idx += N
        
        batch_b = list(map(int, data[idx:idx+N-1]))
        idx += N - 1
        
        # Find the missing package using dictionary (O(N))
        count_a = {}
        for x in batch_a:
            count_a[x] = count_a.get(x, 0) + 1
        
        count_b = {}
        for x in batch_b:
            count_b[x] = count_b.get(x, 0) + 1
        
        # Find the package that's different
        for x in count_a:
            if count_a[x] != count_b.get(x, 0):
                # Find index in batch_a
                for i, val in enumerate(batch_a):
                    if val == x:
                        results.append(str(i))
                        break
                break
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
