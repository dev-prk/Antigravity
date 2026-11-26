import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    R = int(line.strip())
    for i in range(1, R + 1):
        start = R - i + 1
        row = list(range(start, R + 1))
        # fill remaining positions with R
        while len(row) < R:
            row.append(R)
        print(' '.join(map(str, row)))

if __name__ == "__main__":
    main()
