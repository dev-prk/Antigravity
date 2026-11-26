import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print("")
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if n == 1:
        print(str(arr[0]))
        print(str(arr[0]))
        return
    
    # Find star elements (strictly greater than all elements on its right)
    stars = []
    max_right = arr[-1]
    stars.append(max_right)
    
    for i in range(n - 2, -1, -1):
        if arr[i] > max_right:
            stars.append(arr[i])
            max_right = arr[i]
    
    stars.reverse()
    
    # Find super star elements (strictly greater than all elements on both sides)
    # A super star must be the global maximum and appear exactly once
    max_val = max(arr)
    count_max = arr.count(max_val)
    
    super_stars = []
    if count_max == 1:
        super_stars.append(max_val)
    
    # Output
    print(' '.join(map(str, stars)))
    if super_stars:
        print(' '.join(map(str, super_stars)))
    else:
        print(-1)

if __name__ == "__main__":
    main()
