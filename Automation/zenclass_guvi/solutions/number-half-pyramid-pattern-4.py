import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    R = int(data[0])
    lines = []
    for i in range(1, R + 1):
        start = R - i + 1
        lines.append(''.join(str(n) for n in range(start, R + 1)))
    sys.stdout.write('\n'.join(lines))

main()
