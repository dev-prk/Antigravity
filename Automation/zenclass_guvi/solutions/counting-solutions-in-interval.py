import sys
import math

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    
    parts = line.split(',')
    params = {}
    for part in parts:
        key, value = part.split('=')
        params[key.strip()] = int(value.strip())
    
    a = params['a']
    b = params['b']
    c = params['c']
    X = params['X']
    Y = params['Y']
    
    if a == 0 and b == 0:
        print(1 if c == 0 else 0)
        return
    
    if a == 0:
        if c % b == 0:
            y_val = c // b
            if 0 <= y_val <= Y:
                print(X + 1)
            else:
                print(0)
        else:
            print(0)
        return
    
    if b == 0:
        if c % a == 0:
            x_val = c // a
            if 0 <= x_val <= X:
                print(Y + 1)
            else:
                print(0)
        else:
            print(0)
        return
    
    if c % math.gcd(a, b) != 0:
        print(0)
        return
    
    if a < 0 or b < 0:
        print(0)
        return
    
    count = 0
    for x in range(X + 1):
        remainder = c - a * x
        if remainder < 0:
            break
        if remainder % b == 0:
            y = remainder // b
            if 0 <= y <= Y:
                count += 1
    
    print(count)

if __name__ == "__main__":
    main()
