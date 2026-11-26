import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    n = int(data[0])
    m = int(data[1])
    idx = 2

    arr = []
    if n > 0:
        arr.extend(map(int, data[idx:idx + n]))
        idx += n
    if m > 0:
        arr.extend(map(int, data[idx:idx + m]))

    arr.sort()
    sys.stdout.write(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
