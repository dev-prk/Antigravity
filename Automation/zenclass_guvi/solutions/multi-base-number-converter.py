def decimal_to_binary(n):
    return bin(n)[2:]

def decimal_to_octal(n):
    return oct(n)[2:]

def decimal_to_hex(n):
    return hex(n)[2:]

def binary_to_decimal(s):
    return int(s, 2)

def octal_to_decimal(s):
    return int(s, 8)

def hex_to_decimal(s):
    return int(s, 16)

def convert(value, c1, c2):
    if c1 == 1:
        decimal_val = int(value)
    elif c1 == 2:
        decimal_val = binary_to_decimal(value)
    elif c1 == 3:
        decimal_val = octal_to_decimal(value)
    elif c1 == 4:
        decimal_val = hex_to_decimal(value)
    else:
        return "-1"
    
    if c2 == 1:
        return str(decimal_val)
    elif c2 == 2:
        return decimal_to_binary(decimal_val)
    elif c2 == 3:
        return decimal_to_octal(decimal_val)
    elif c2 == 4:
        return decimal_to_hex(decimal_val)
    else:
        return "-1"

import sys

def main():
    lines = sys.stdin.read().strip().split('\n')
    if len(lines) < 2:
        print(-1)
        return
    
    try:
        c1, c2 = map(int, lines[0].strip().split())
        value = lines[1].strip()
        result = convert(value, c1, c2)
        print(result)
    except:
        print(-1)

if __name__ == "__main__":
    main()
