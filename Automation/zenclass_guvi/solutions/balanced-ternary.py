import sys

def to_balanced_ternary(n):
    if n == 0:
        return "0"
    
    digits = []
    while n != 0:
        remainder = n % 3
        n = n // 3
        
        if remainder == 2:
            remainder = -1
            n += 1
        elif remainder == -1:
            digits.append('T')
            continue
        
        digits.append(str(remainder))
    
    return ''.join(reversed(digits)) if digits else "0"

def solve():
    data = sys.stdin.read().strip()
    if not data:
        print("0")
        return
    
    if '=' in data:
        n = int(data.split('=')[1])
    else:
        n = int(data)
    
    print(to_balanced_ternary(n))

if __name__ == "__main__":
    solve()
