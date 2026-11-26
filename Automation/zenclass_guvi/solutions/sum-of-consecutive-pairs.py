import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n <= 0 or len(data) < 1:
        print(0)
        return
    
    arr = list(map(int, data[1:1+n]))
    
    if len(arr) < 2:
        print(0)
        return
    
    total = 0
    for i in range(len(arr) - 1):
        total += arr[i] + arr[i+1]
    
    print(total)

if __name__ == "__main__":
    main()
