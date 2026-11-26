import sys
import math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('no')
        return
    
    P = int(data[0])
    A = int(data[1])
    
    # For a rectangle with sides x and y:
    # Perimeter P = 2(x + y) => x + y = P/2
    # Area A = x * y
    # So x and y are roots of: t^2 - (P/2)*t + A = 0
    # For real roots: (P/2)^2 - 4A >= 0
    # For integer roots: roots must be integers
    
    # Check if P is even (for integer sum x + y)
    if P % 2 != 0:
        print('no')
        return
    
    s = P // 2  # x + y
    
    # Check discriminant
    disc = s * s - 4 * A
    
    if disc < 0:
        print('no')
        return
    
    # Check if discriminant is a perfect square
    sqrt_disc = int(math.sqrt(disc))
    if sqrt_disc * sqrt_disc != disc:
        print('no')
        return
    
    # Check if (s - sqrt_disc) is even and non-negative
    # x = (s - sqrt_disc) / 2, y = (s + sqrt_disc) / 2
    diff = s - sqrt_disc
    
    if diff < 0 or diff % 2 != 0:
        print('no')
        return
    
    x = diff // 2
    y = (s + sqrt_disc) // 2
    
    if x > 0 and y > 0:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
