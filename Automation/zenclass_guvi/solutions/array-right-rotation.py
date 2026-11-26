import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0:
        print()
        return
    
    arr = list(map(int, data[2:2+n]))
    
    if n > 0:
        k = k % n
    
    if k == 0:
        print(' '.join(map(str, arr)))
        return
    
    result = [0] * n
    for i in range(n):
        result[(i + k) % n] = arr[i]
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
