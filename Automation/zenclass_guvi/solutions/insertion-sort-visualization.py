import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    arr = list(map(int, data[1:n+1]))
    
    if n == 0:
        return
    
    # Print initial array
    print(' '.join(map(str, arr)))
    
    # Perform insertion sort
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        
        # Shift elements greater than key to the right
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        
        arr[j + 1] = key
        
        # Print current state after each insertion
        print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
