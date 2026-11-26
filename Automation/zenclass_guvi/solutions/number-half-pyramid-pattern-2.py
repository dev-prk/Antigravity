import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    r = int(data[0])
    lines = []
    for i in range(1, r + 1):
        lines.append(''.join(str(j) for j in range(i, r + 1)))
    sys.stdout.write('\n'.join(lines))

if __name__ == "__main__":
    main()
