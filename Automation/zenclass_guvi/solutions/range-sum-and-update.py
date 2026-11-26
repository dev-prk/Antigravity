import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    arr = list(map(int, data[idx:idx+n]))
    idx += n
    
    q = int(data[idx])
    idx += 1
    
    # Build prefix sum for efficient range sum queries
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]
    
    # Track pending updates: updates[(l, r)] = z
    # This stores "add z to range [l, r]"
    updates = {}
    
    output = []
    
    for _ in range(q):
        op = int(data[idx])
        idx += 1
        
        if op == 1:
            x = int(data[idx])
            idx += 1
            y = int(data[idx])
            idx += 1
            z = int(data[idx])
            idx += 1
            
            # x and y are 1-indexed
            l = x - 1
            r = y - 1
            
            # Store this update
            if (l, r) in updates:
                updates[(l, r)] += z
            else:
                updates[(l, r)] = z
        else:
            x = int(data[idx])
            idx += 1
            y = int(data[idx])
            idx += 1
            
            # x and y are 1-indexed
            l = x - 1
            r = y - 1
            
            # Calculate base sum using prefix sum
            total = prefix[r + 1] - prefix[l]
            
            # Add contributions from all pending updates that overlap with [l, r]
            for (ul, ur), z in updates.items():
                # Find overlap
                ol = max(l, ul)
                orr = min(r, ur)
                if ol <= orr:
                    total += z * (orr - ol + 1)
            
            output.append(str(total))
    
    print('\n'.join(output))

if __name__ == "__main__":
    main()
