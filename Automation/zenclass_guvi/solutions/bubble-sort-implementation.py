import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    arr = list(map(int, data[1:n+1]))
    
    # Make a copy to work with
    arr = arr[:]
    
    # Perform n passes (not n-1)
    for i in range(n):
        # Each pass goes from 0 to n-i-2 (comparing adjacent pairs)
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
        
        # Print after each pass
        print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
