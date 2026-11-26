import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    if len(data) < n + 1:
        print(-1)
        return
    
    result = []
    for i in range(n):
        num = int(data[i + 1])
        if num == i:
            result.append(num)
    
    if not result:
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
