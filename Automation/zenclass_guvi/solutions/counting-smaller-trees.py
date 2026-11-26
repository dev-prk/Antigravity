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
    
    heights = list(map(int, data[1:n+1]))
    
    min_height = min(heights)
    count = sum(1 for h in heights if h == min_height)
    
    print(count)

if __name__ == "__main__":
    main()
