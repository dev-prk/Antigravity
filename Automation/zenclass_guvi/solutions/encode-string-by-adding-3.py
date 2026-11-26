import sys

def main():
    S = sys.stdin.read().strip()
    if not S:
        return
    result = []
    for ch in S:
        # Only uppercase English letters are expected based on samples
        code = ord(ch)
        # Wrap around A-Z
        new_code = code + 3
        if new_code > ord('Z'):
            new_code -= 26
        result.append(chr(new_code))
    print(''.join(result))

if __name__ == '__main__':
    main()
