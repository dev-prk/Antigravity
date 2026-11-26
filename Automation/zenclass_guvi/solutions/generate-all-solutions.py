import sys
import math

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

def solve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        a = int(parts[0].split('=')[1])
        b = int(parts[1].split('=')[1])
        c = int(parts[2].split('=')[1])
        L = int(parts[3].split('=')[1])
        R = int(parts[4].split('=')[1])
        
        gcd = math.gcd(abs(a), abs(b))
        if gcd == 0:
            if c == 0:
                if L <= 0 <= R:
                    print(0, 0)
                else:
                    print(-1)
            else:
                print(-1)
            continue
        
        if c % gcd != 0:
            print(-1)
            continue
        
        if a == 0 and b == 0:
            if c == 0:
                if L <= 0 <= R:
                    print(0, 0)
                else:
                    print(-1)
            else:
                print(-1)
            continue
        
        if a == 0:
            if b == 0:
                print(-1)
                continue
            if c % b == 0:
                y0 = c // b
                if isinstance(y0, int) and L <= 0 <= R:
                    print(0, int(y0))
                else:
                    print(-1)
            else:
                print(-1)
            continue
        
        if b == 0:
            if a == 0:
                print(-1)
                continue
            if c % a == 0:
                x0 = c // a
                if isinstance(x0, int) and L <= int(x0) <= R:
                    print(int(x0), 0)
                else:
                    print(-1)
            else:
                print(-1)
            continue
        
        gcd, x0, y0 = extended_gcd(a, b)
        x0 = x0 * (c // gcd)
        y0 = y0 * (c // gcd)
        
        solutions = []
        for x in range(L, R + 1):
            if a * x + b * y0 == c % gcd:
                pass
        
        t_min = (L - x0) // (b // gcd)
        if (L - x0) % (b // gcd) != 0:
            t_min += 1
        
        t_max = (R - x0) // (b // gcd)
        
        if b // gcd > 0:
            t_start = t_min
            t_end = t_max
        else:
            t_start = t_max
            t_end = t_min
        
        for t in range(t_start, t_end + 1):
            x = x0 + t * (b // gcd)
            y = y0 - t * (a // gcd)
            if L <= x <= R:
                solutions.append((x, y))
        
        if solutions:
            x, y = solutions[0]
            print(x, y)
        else:
            print(-1)

if __name__ == "__main__":
    solve()
