import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    L, R = int(data[0]), int(data[1])
    
    if R < 2:
        print(0)
        return
    
    # Compute sum of proper divisors for all numbers up to R
    s = [0] * (R + 1)
    for i in range(1, R // 2 + 1):
        for j in range(2 * i, R + 1, i):
            s[j] += i
    
    # Count ideal couples (a, b) where L <= a < b <= R, s(a) = b, and s(b) = a
    count = 0
    for a in range(L, R + 1):
        if a >= len(s):
            continue
        b = s[a]
        if a < b <= R and b < len(s) and s[b] == a:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
