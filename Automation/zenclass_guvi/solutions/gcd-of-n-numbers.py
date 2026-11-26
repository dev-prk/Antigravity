import sys
import math

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
    
    numbers = list(map(int, data[1:n+1]))
    
    if not numbers:
        print(-1)
        return
    
    result = abs(numbers[0])
    
    for i in range(1, len(numbers)):
        if result == 0:
            result = abs(numbers[i])
        else:
            result = math.gcd(result, abs(numbers[i]))
    
    if result == 0:
        print(-1)
    else:
        print(result)

if __name__ == "__main__":
    main()
