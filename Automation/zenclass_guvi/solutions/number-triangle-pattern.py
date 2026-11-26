import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        return
    lines = []
    for i in range(1, n + 1):
        num = n - i + 1
        spaces = n - i
        line = " " * spaces + str(num) * i
        lines.append(line)
    sys.stdout.write("\n".join(lines))

if __name__ == "__main__":
    main()
