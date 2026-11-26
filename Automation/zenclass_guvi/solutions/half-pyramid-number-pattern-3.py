import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    r = int(data[0])
    lines = []
    for i in range(1, r + 1):
        start = 1 if i % 2 == 1 else 2
        row = [str(start + 2 * j) for j in range(i)]
        lines.append(' '.join(row))
    if lines:
        sys.stdout.write('\n'.join(lines) + '\n')

if __name__ == '__main__':
    main()
