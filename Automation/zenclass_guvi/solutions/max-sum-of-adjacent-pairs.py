import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    total = 0
    for i in range(n - 1):
        total += max(arr[i], arr[i+1])
    
    print(total)

if __name__ == "__main__":
    main()
