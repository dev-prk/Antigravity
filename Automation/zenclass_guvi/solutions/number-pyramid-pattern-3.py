import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    R = int(data[0].strip())
    for i in range(1, R + 1):
        val = 2 * (R - i) + 1
        spaces = ' ' * (i - 1)
        print(spaces + str(val) * val)

if __name__ == "__main__":
    main()
