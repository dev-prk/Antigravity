import sys

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Deterministic Miller-Rabin witnesses for 64-bit numbers
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    for a in witnesses:
        if a >= n:
            continue
        
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        line = line.split('=')[1]
    
    try:
        n = int(line)
    except:
        print("false")
        return
    
    result = is_prime(n)
    print("true" if result else "false")

if __name__ == "__main__":
    main()
