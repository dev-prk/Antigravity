import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0 or k <= 0 or k > n:
        print(-1)
        return
    
    if len(data) < 2 + n:
        print(-1)
        return
    
    elements = list(map(int, data[2:2+n]))
    # Get unique elements and sort
    unique_sorted = sorted(set(elements))
    
    # Check if Kth smallest exists in unique elements
    if k > len(unique_sorted):
        print(-1)
    else:
        print(unique_sorted[k-1])

if __name__ == "__main__":
    main()
