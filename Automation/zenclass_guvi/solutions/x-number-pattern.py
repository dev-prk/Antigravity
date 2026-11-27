import sys

def main():
    n = int(sys.stdin.readline().strip())
    lines = []
    for i in range(1, n + 1):
        if i == n:
            line = ' ' * (n - 1) + str(i)
        else:
            line = ' ' * (i - 1) + str(i) + ' ' * (2 * n - 2 * i - 1) + str(i)
        lines.append(line)
    for i in range(n - 1, 0, -1):
        if i == n:
            line = ' ' * (n - 1) + str(i)
        else:
            line = ' ' * (i - 1) + str(i) + ' ' * (2 * n - 2 * i - 1) + str(i)
        lines.append(line)
    for line in lines:
        print(line)

if __name__ == "__main__":
    main()
