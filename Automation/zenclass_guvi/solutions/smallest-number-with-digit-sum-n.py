import sys

def smallest_number_with_digit_sum(n):
    if n == 0:
        return 0
    
    # The smallest number will have as few digits as possible
    # Start with the minimum number of digits
    num_digits = (n + 8) // 9  # Ceiling division by 9
    
    # Build the number from left to right
    # First digit should be as small as possible but non-zero
    # Remaining digits should be as large as possible (to minimize the number)
    
    result = []
    remaining_sum = n
    remaining_digits = num_digits
    
    for i in range(num_digits):
        # For the first digit, minimum is 1
        # For other digits, minimum is 0
        min_digit = 1 if i == 0 else 0
        
        # The digit should be large enough so that remaining sum can be distributed
        # among remaining digits (each at most 9)
        max_possible_for_rest = 9 * (remaining_digits - 1)
        digit = max(min_digit, remaining_sum - max_possible_for_rest)
        
        result.append(str(digit))
        remaining_sum -= digit
        remaining_digits -= 1
    
    return int(''.join(result))

def main():
    n = int(sys.stdin.readline().strip())
    print(smallest_number_with_digit_sum(n))

if __name__ == "__main__":
    main()
