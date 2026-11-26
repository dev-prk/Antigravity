import sys

def divide_big_int(num_str, divisor):
    if divisor == 0:
        return "Division by zero"
    
    # Handle negative numbers
    negative = False
    if num_str[0] == '-':
        negative = True
        num_str = num_str[1:]
    
    # Remove leading zeros
    num_str = num_str.lstrip('0')
    if not num_str:
        return "0"
    
    if divisor < 0:
        negative = not negative
        divisor = -divisor
    
    # Perform division digit by digit
    result = []
    remainder = 0
    
    for digit in num_str:
        current = remainder * 10 + int(digit)
        quotient_digit = current // divisor
        remainder = current % divisor
        if result or quotient_digit != 0:
            result.append(str(quotient_digit))
    
    if not result:
        result.append('0')
    
    result_str = ''.join(result)
    if negative:
        result_str = '-' + result_str
    
    return result_str

def main():
    line = sys.stdin.readline().strip()
    
    # Parse input: a=123456,b=3
    if '=' in line and ',' in line:
        parts = line.split(',')
        a_part = parts[0].split('=')
        b_part = parts[1].split('=')
        a = a_part[1]
        b = int(b_part[1])
    else:
        # Try to parse as two values separated by space or comma
        parts = line.replace(',', ' ').split()
        if len(parts) >= 2:
            a = parts[0]
            b = int(parts[1])
        else:
            print("Invalid input")
            return
    
    result = divide_big_int(a, b)
    print(result)

if __name__ == "__main__":
    main()
