import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    it = iter(data)
    try:
        r = int(next(it))
        c = int(next(it))
    except StopIteration:
        return

    vals = []
    for _ in range(r * c):
        try:
            vals.append(int(next(it)))
        except StopIteration:
            break

    if r == 0 or c == 0 or not vals:
        return

    matrix = [vals[i * c:(i + 1) * c] for i in range(r)]
    for row in zip(*matrix):
        print(' '.join(map(str, row)))

if __name__ == '__main__':
    main()
