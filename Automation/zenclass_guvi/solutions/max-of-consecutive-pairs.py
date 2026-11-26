import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    n = int(data[0])
    if n <= 1:
        return

    values = list(map(int, data[1:1 + n]))
    result = [max(values[i], values[i + 1]) for i in range(n - 1)]

    if result:
        sys.stdout.write(" ".join(map(str, result)) + "\n")

if __name__ == "__main__":
    main()
