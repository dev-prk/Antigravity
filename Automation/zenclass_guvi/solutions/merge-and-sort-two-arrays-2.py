import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 and m == 0:
        print("")
        return
    
    idx = 2
    arr1 = list(map(int, data[idx:idx+n]))
    idx += n
    arr2 = list(map(int, data[idx:idx+m]))
    
    arr1.sort()
    arr2.sort(reverse=True)
    
    result = arr1 + arr2
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
