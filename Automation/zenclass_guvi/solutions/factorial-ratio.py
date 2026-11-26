import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    parts = line.strip().split()
    a = int(parts[0])
    b = int(parts[1])
    
    if a < 0 or b < 0:
        print(-1)
        return
    
    if a < b:
        print(-1)
        return
    
    result = 1
    for i in range(b + 1, a + 1):
        result *= i
    
    print(result)

if __name__ == "__main__":
    main()
