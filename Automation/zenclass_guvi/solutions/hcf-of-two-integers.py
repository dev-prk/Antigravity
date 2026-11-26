import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(-1)
        return
    parts = line.split()
    if len(parts) < 2:
        print(-1)
        return
    try:
        a = int(parts[0])
        b = int(parts[1])
    except ValueError:
        print(-1)
        return
    
    a = abs(a)
    b = abs(b)
    
    if a == 0 and b == 0:
        print(-1)
        return
    
    if a == 0:
        print(b)
        return
    
    if b == 0:
        print(a)
        return
    
    smaller = min(a, b)
    
    for i in range(smaller, 0, -1):
        if a % i == 0 and b % i == 0:
            print(i)
            return

if __name__ == "__main__":
    main()
