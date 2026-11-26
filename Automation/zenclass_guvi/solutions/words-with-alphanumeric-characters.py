import sys

def main():
    data = sys.stdin.read().split()
    result = []
    for word in data:
        has_alpha = any(c.isalpha() for c in word)
        has_digit = any(c.isdigit() for c in word)
        if has_alpha and has_digit:
            result.append(word)
    print(' '.join(result))

if __name__ == "__main__":
    main()
