import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    m = int(data[2])
    a = list(map(int, data[3:3+n]))
    
    if n == 0:
        print(0.0)
        return
    
    a.sort()
    
    # Prefix sums
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i+1] = prefix[i] + a[i]
    
    best_avg = float(a[0])
    
    for keep in range(1, n + 1):
        # We keep the last 'keep' elements (indices n-keep to n-1)
        # These are the largest 'keep' elements
        
        if keep == 1:
            # Only one superhero
            # All operations go to increase its power
            max_increases = min(k, m)
            avg = a[n-1] + max_increases
            best_avg = max(best_avg, avg)
        else:
            # For keep >= 2, we need at least 1 remove operation
            remove_ops = n - keep
            if remove_ops > m:
                continue
            
            remaining_ops = m - remove_ops
            # remaining_ops can be used for power increases
            
            increase_ops = min(remaining_ops, keep * k)
            
            # Calculate average
            sum_kept = prefix[n] - prefix[n-keep]
            avg = (sum_kept + increase_ops) / keep
            best_avg = max(best_avg, avg)
    
    print(f"{best_avg:.10g}")

if __name__ == "__main__":
    main()
