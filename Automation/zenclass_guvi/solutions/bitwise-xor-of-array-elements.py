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
    
    elements = list(map(int, data[1:n+1]))
    result = 0
    for elem in elements:
        result ^= elem
    
    print(result)

if __name__ == "__main__":
    main()
