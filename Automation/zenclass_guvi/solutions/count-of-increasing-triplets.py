import sys

def count_increasing_triplets(arr):
    n = len(arr)
    if n < 3:
        return -1
    
    count = 0
    
    for j in range(1, n - 1):
        smaller = 0
        for i in range(j):
            if arr[i] < arr[j]:
                smaller += 1
        
        greater = 0
        for k in range(j + 1, n):
            if arr[k] > arr[j]:
                greater += 1
        
        count += smaller * greater
    
    return count if count > 0 else -1

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n < 3:
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    result = count_increasing_triplets(arr)
    print(result)

if __name__ == "__main__":
    main()
