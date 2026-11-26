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
    left, right = 0, n - 1
    toggle = True
    
    while left <= right:
        if toggle:
            result.append(arr[right])
            right -= 1
        else:
            result.append(arr[left])
            left += 1
        toggle = not toggle
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
