import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    idx = 0
    n1 = int(data[idx])
    idx += 1
    arr1 = list(map(int, data[idx:idx + n1]))
    idx += n1
    n2 = int(data[idx])
    idx += 1
    arr2 = list(map(int, data[idx:idx + n2]))
    
    # Handle empty arrays
    if n1 == 0 and n2 == 0:
        print(-1)
        return
    if n1 == 0:
        arr1 = []
    if n2 == 0:
        arr2 = []
    
    # Use set to remove duplicates
    union_set = set(arr1) | set(arr2)
    
    if not union_set:
        print(-1)
        return
    
    # Sort and output
    result = sorted(union_set)
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
