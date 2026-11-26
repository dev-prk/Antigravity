import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if n <= 0 or n >= 100:
        print(-1)
        return
    
    if len(data) < n + 1:
        print(-1)
        return
    
    numbers = list(map(int, data[1:n+1]))
    result = [x for x in numbers if x < 15]
    
    if not result:
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
