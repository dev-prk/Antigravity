import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print()
        return
    
    arr = list(map(int, data[1:n+1]))
    arr.sort()
    
    result = []
    left = 0
    right = n - 1
    
    for i in range(n):
        if i % 2 == 0:
            result.append(arr[right])
            right -= 1
        else:
            result.append(arr[left])
            left += 1
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
