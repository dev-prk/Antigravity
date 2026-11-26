import sys

def multiply_strings(a, b):
    if a == "0" or b == "0":
        return "0"
    
    m, n = len(a), len(b)
    result = [0] * (m + n)
    
    for i in range(m - 1, -1, -1):
        digit_a = int(a[i])
        carry = 0
        for j in range(n - 1, -1, -1):
            digit_b = int(b[j])
            product = digit_a * digit_b + result[i + j + 1] + carry
            result[i + j + 1] = product % 10
            carry = product // 10
        result[i] = carry
    
    result_str = ''.join(map(str, result)).lstrip('0')
    return result_str if result_str else "0"

def solve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if '=' in line:
            parts = line.split(',')
            a = parts[0].split('=')[1]
            b = parts[1].split('=')[1]
            result = multiply_strings(a, b)
            print(result)

if __name__ == "__main__":
    solve()
