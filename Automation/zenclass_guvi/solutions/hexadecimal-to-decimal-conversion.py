import sys

def hex_to_decimal(hex_str):
    hex_digits = '0123456789ABCDEF'
    decimal_value = 0
    hex_str = hex_str.upper().strip()
    for i, digit in enumerate(reversed(hex_str)):
        decimal_value += hex_digits.index(digit) * (16 ** i)
    return decimal_value

hex_str = sys.stdin.readline().strip()
print(hex_to_decimal(hex_str))
