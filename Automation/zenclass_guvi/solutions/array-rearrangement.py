def main():
    import sys
    data = sys.stdin.read().split()
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    
    for i in range(n):
        arr[i] += (arr[arr[i] % n] % n) * n
    
    for i in range(n):
        arr[i] = arr[i] // n
    
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
