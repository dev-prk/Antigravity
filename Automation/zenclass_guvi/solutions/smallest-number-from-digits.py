import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    # The input is a number string; may have whitespace around
    s = data.split()[0] if data.split() else data
    # Sort digits
    digits = sorted(s)
    # If all zeros, return as-is (avoids leading zero issues? Actually if all zeros, sorted is all zeros, that's fine)
    if not digits:
        print("")
        return
    # If the first digit is '0', we need to swap with first non-zero digit
    if digits[0] == '0':
        # Find first non-zero
        i = 0
        while i < len(digits) and digits[i] == '0':
            i += 1
        if i < len(digits):
            digits[0], digits[i] = digits[i], digits[0]
    print(''.join(digits))

if __name__ == "__main__":
    main()
