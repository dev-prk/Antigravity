import sys

def add_without_carry(a, b):
    result = 0
    base = 1
    while a > 0 or b > 0:
        digit_a = a % 10
        digit_b = b % 10
        sum_digit = (digit_a + digit_b) % 10
        result += sum_digit * base
        base *= 10
        a //= 10
        b //= 10
    return result

def main():
    line = sys.stdin.readline()
    if not line:
        return
    parts = line.strip().split()
    if len(parts) < 2:
        return
    try:
        a = int(parts[0])
        b = int(parts[1])
    except ValueError:
        return
    
    # Handle negative numbers
    sign_a = 1 if a >= 0 else -1
    sign_b = 1 if b >= 0 else -1
    
    abs_a = abs(a)
    abs_b = abs(b)
    
    # Add without carry for absolute values
    sum_abs = add_without_carry(abs_a, abs_b)
    
    # Determine the sign of the result
    if sign_a == sign_b:
        result = sign_a * sum_abs
    else:
        # Different signs - subtract
        if abs_a >= abs_b:
            result = sign_a * sum_abs
        else:
            result = sign_b * sum_abs
    
    print(result)

if __name__ == "__main__":
    main()
