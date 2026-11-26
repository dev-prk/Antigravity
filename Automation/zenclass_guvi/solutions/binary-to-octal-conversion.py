import sys

def binary_to_octal(binary_str):
    # Remove any leading/trailing whitespace and handle empty string
    binary_str = binary_str.strip()
    if not binary_str:
        return "0"
    
    # Handle all zeros case
    if set(binary_str) == {'0'}:
        return "0"
    
    # Remove leading zeros
    binary_str = binary_str.lstrip('0')
    
    # If string becomes empty after removing leading zeros, it was all zeros
    if not binary_str:
        return "0"
    
    # Pad with leading zeros to make length multiple of 3
    padding_needed = (3 - len(binary_str) % 3) % 3
    binary_str = '0' * padding_needed + binary_str
    
    # Convert each group of 3 bits to octal digit
    octal_digits = []
    for i in range(0, len(binary_str), 3):
        group = binary_str[i:i+3]
        # Convert 3-bit binary to decimal
        decimal_value = int(group[0]) * 4 + int(group[1]) * 2 + int(group[2]) * 1
        octal_digits.append(str(decimal_value))
    
    return ''.join(octal_digits)

def main():
    # Read input from stdin
    binary_input = sys.stdin.read().strip()
    
    # Convert and print result
    result = binary_to_octal(binary_input)
    print(result)

if __name__ == "__main__":
    main()
