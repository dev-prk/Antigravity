import sys
import math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    degree = int(data[0])
    n_terms = int(data[1])
    
    x_rad = math.radians(degree)
    
    total = 0.0
    for i in range(n_terms):
        term = ((-1) ** i) * (x_rad ** (2 * i + 1)) / math.factorial(2 * i + 1)
        total += term
    
    print(f"{total:.2f}")

if __name__ == "__main__":
    main()
