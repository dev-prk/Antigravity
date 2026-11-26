import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split(',')
    a = int(parts[0].split('=')[1])
    b = int(parts[1].split('=')[1])
    m = int(parts[2].split('=')[1])
    
    if m == 1:
        print(0)
        return
    
    result = 1
    base = a % m
    
    while b > 0:
        if b % 2 == 1:
            result = (result * base) % m
        base = (base * base) % m
        b //= 2
    
    print(result)

if __name__ == "__main__":
    main()
