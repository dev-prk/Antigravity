import sys

def main():
    s = sys.stdin.readline().strip()
    
    if not s:
        print("Right")
        return
    
    n = len(s)
    total_sum = 0
    
    for i in range(n):
        digit = int(s[i])
        if digit > 0:
            term = digit
            for j in range(1, digit):
                term *= (digit - j)
            total_sum += term
        elif digit == 0:
            continue
    
    predicted = int(s)
    
    if total_sum == predicted:
        print("Right")
    else:
        print("Wrong")

if __name__ == "__main__":
    main()
