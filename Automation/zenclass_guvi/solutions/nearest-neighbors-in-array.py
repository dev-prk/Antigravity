import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    arr = list(map(int, data[2:2+n]))
    
    # Create list of (difference, value, original_index)
    diff_with_val = [(abs(x - k), x, i) for i, x in enumerate(arr)]
    
    # Sort by difference first, then by original index for ties
    diff_with_val.sort(key=lambda x: (x[0], x[2]))
    
    # Get top 3 nearest neighbors, excluding K itself if present
    result = []
    for d, val, i in diff_with_val:
        if val != k:
            result.append(str(val))
            if len(result) == 3:
                break
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
