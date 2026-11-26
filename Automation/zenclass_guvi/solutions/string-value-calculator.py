import sys

def calculate_string_value(s):
    total = 0
    for char in s:
        if 'a' <= char <= 'z':
            position = ord(char) - ord('a') + 1
            total += position if position % 2 == 1 else -position
    return total

def main():
    input = sys.stdin.read().splitlines()
    n = int(input[0])
    for i in range(1, n + 1):
        s = input[i]
        print(calculate_string_value(s))

if __name__ == "__main__":
    main()
