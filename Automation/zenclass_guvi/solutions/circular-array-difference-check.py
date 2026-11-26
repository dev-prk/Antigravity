import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0:
        print("")
        return
    
    arr = list(map(int, data[2:2+n]))
    
    result = []
    for i in range(n):
        next_idx = (i + 1) % n
        diff = abs(arr[next_idx] - arr[i])
        if diff > m:
            result.append('1')
        else:
            result.append('0')
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
