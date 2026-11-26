import sys

def next_greater_number(n_str):
    digits = list(n_str)
    n = len(digits)
    
    # Step 1: Find the largest index i such that digits[i] < digits[i+1]
    i = n - 2
    while i >= 0 and digits[i] >= digits[i + 1]:
        i -= 1
    
    # If no such index exists, the number is the largest possible
    if i < 0:
        return "impossible"
    
    # Step 2: Find the largest index j > i such that digits[j] > digits[i]
    j = n - 1
    while digits[j] <= digits[i]:
        j -= 1
    
    # Step 3: Swap digits[i] and digits[j]
    digits[i], digits[j] = digits[j], digits[i]
    
    # Step 4: Reverse the suffix starting from i+1
    digits[i + 1:] = reversed(digits[i + 1:])
    
    return ''.join(digits)

# Read input
n_str = sys.stdin.readline().strip()

# Find and print the next greater number
result = next_greater_number(n_str)
print(result)
