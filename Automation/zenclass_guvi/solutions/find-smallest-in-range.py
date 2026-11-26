import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    l = int(data[1])
    r = int(data[2])
    
    if n == 0 or len(data) < 3 + n:
        print(-1)
        return
    
    numbers = list(map(int, data[3:3+n]))
    
    smallest = None
    for num in numbers:
        if l <= num <= r:
            if smallest is None or num < smallest:
                smallest = num
    
    if smallest is None:
        print(-1)
    else:
        print(smallest)

if __name__ == "__main__":
    main()
