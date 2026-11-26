import sys

def main():
    # Read the entire input, stripping only trailing newline(s) but preserving internal spaces
    data = sys.stdin.read()
    # Remove trailing newlines and spaces? The problem says "sentence as string".
    # Typically, we should treat the whole input as the string.
    # However, sample shows "Hello how are you" -> "uoy era woh olleH"
    # So we just reverse whatever we read. But be careful about trailing newline.
    s = data.rstrip('\n').rstrip('\r')
    print(s[::-1])

if __name__ == '__main__':
    main()
