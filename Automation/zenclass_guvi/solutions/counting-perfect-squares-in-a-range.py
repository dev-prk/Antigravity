import sys
import math

def main():
    line = sys.stdin.readline()
    if not line:
        return
    parts = line.split()
    L = int(parts[0])
    R = int(parts[1])
    
    start = math.isqrt(L)
    if start * start < L:
        start += 1
    
    end = math.isqrt(R)
    
    count = end - start + 1
    
    if count <= 0:
        print(-1)
    else:
        print(count)

if __name__ == "__main__":
    main()
