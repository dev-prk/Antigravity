import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    digits = list(map(int, data[1:1+n]))
    
    if n == 0:
        print("1")
        return
    
    # Add 1 to the number represented by the digits
    carry = 1
    for i in range(n - 1, -1, -1):
        digits[i] += carry
        carry = digits[i] // 10
        digits[i] %= 10
        if carry == 0:
            break
    
    if carry:
        # Need to add a new digit at the beginning
        digits.insert(0, 1)
    
    # Remove leading zeros if any (though shouldn't happen with proper addition)
    while len(digits) > 1 and digits[0] == 0:
        digits.pop(0)
    
    print(' '.join(map(str, digits)))

if __name__ == "__main__":
    main()
