import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    for i in range(1, R + 1):
        print(' ' * (R - i) + '*' * i)

if __name__ == "__main__":
    main()
