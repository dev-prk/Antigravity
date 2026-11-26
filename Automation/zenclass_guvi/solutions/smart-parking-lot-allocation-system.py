import sys
import bisect

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    Q = int(data[idx])
    idx += 1
    
    occupied = set()
    
    results = []
    
    for _ in range(Q):
        op = data[idx]
        idx += 1
        
        if op == 'A':
            x = int(data[idx])
            idx += 1
            
            found = -1
            for slot in range(x, N + 1):
                if slot not in occupied:
                    found = slot
                    break
            
            if found == -1:
                results.append("-1")
            else:
                occupied.add(found)
                results.append(str(found))
                
        elif op == 'F':
            x = int(data[idx])
            idx += 1
            if x in occupied:
                occupied.remove(x)
                
        elif op == 'L':
            if not occupied:
                results.append(str(N))
            else:
                sorted_occ = sorted(occupied)
                max_block = 0
                
                max_block = max(max_block, sorted_occ[0] - 1)
                
                for i in range(len(sorted_occ) - 1):
                    gap = sorted_occ[i + 1] - sorted_occ[i] - 1
                    max_block = max(max_block, gap)
                
                max_block = max(max_block, N - sorted_occ[-1])
                
                results.append(str(max_block))
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
