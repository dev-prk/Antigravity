import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return

    R = int(data[0])
    lines = []

    for i in range(1, R + 1):
        if i % 2 == 1:
            line = ''.join(str(2 * j + 1) for j in range(i))
        else:
            line = ''.join(str(2 * j + 2) for j in range(i))
        lines.append(line)

    if lines:
        sys.stdout.write('\n'.join(lines) + '\n')

if __name__ == '__main__':
    main()
