import sys

def main():
    s = sys.stdin.readline()
    if s.endswith('\n'):
        s = s[:-1]
    parts = s.split(' ')
    reversed_parts = [p[::-1] for p in parts]
    result = ' '.join(reversed_parts)
    print(result)

if __name__ == "__main__":
    main()
