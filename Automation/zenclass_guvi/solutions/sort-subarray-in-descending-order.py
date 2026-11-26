import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    i1, i2 = int(data[1+n]), int(data[2+n])
    
    # Sort subarray from i1 to i2 (inclusive) in descending order
    sub = arr[i1:i2+1]
    sub.sort(reverse=True)
    arr[i1:i2+1] = sub
    
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
