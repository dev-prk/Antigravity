import sys
import math

def compute_phi(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    
    result = n
    temp = n
    
    if temp % 2 == 0:
        result //= 2
        result *= 1
        while temp % 2 == 0:
            temp //= 2
    
    for i in range(3, int(math.sqrt(temp)) + 1, 2):
        if temp % i == 0:
            result = result // i * (i - 1)
            while temp % i == 0:
                temp //= i
    
    if temp > 1:
        result = result // temp * (temp - 1)
    
    return result

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        line = line.split('=')[1]
    n = int(line)
    print(compute_phi(n))

if __name__ == "__main__":
    main()
