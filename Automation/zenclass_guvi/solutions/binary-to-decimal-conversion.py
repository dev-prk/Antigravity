import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    s = data[0].strip()
    if s == '':
        return
    # Convert binary string to decimal
    print(int(s, 2))

if __name__ == "__main__":
    main()
