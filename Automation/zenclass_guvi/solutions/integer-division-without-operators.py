def divide(A, B):
    if A == 0:
        return 0
    
    INT_MAX = 2**31 - 1
    INT_MIN = -2**31
    
    negative = (A < 0) ^ (B < 0)
    
    A_abs = abs(A)
    B_abs = abs(B)
    
    quotient = 0
    
    while A_abs >= B_abs:
        temp = B_abs
        multiple = 1
        
        while (temp << 1) <= A_abs:
            temp <<= 1
            multiple <<= 1
        
        A_abs -= temp
        quotient += multiple
    
    if negative:
        quotient = -quotient
    
    if quotient > INT_MAX:
        return INT_MAX
    
    return quotient

def main():
    import sys
    data = sys.stdin.read().split()
    A = int(data[0])
    B = int(data[1])
    print(divide(A, B))

if __name__ == "__main__":
    main()
