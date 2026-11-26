import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    if n == 1:
        print(-1)
        return
    
    if len(data) < 2:
        print(-1)
        return
    
    arr = list(map(int, data[1:1+n]))
    
    if len(arr) < 2:
        print(-1)
        return
    
    max_val = max(arr)
    
    second_max = None
    for x in arr:
        if x < max_val:
            if second_max is None or x > second_max:
                second_max = x
    
    if second_max is None:
        print(-1)
    else:
        print(second_max)

if __name__ == "__main__":
    main()
