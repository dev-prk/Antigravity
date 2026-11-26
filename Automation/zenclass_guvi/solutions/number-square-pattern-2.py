import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    R = int(line.strip())
    n = 2 * R - 1
    for i in range(1, n + 1):
        if i <= R:
            numbers = [str(j * j) for j in range(1, i + 1)]
        else:
            numbers = [str(j * j) for j in range(1, 2 * R - i + 1)]
        print(' '.join(numbers))

if __name__ == "__main__":
    main()
