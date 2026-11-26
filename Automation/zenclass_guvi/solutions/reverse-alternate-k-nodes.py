import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    values = []
    idx = 1
    if n > 0 and len(data) >= 1 + n:
        values = list(map(int, data[1:1 + n]))
    # read K
    k_idx = 1 + n
    k = 1
    if k_idx < len(data):
        k = int(data[k_idx])
    if k <= 0:
        sys.stdout.write(' '.join(map(str, values)))
        return
    res = []
    group = 0
    for i in range(0, len(values), k):
        chunk = values[i:i + k]
        if group % 2 == 0:
            res.extend(chunk[::-1])
        else:
            res.extend(chunk)
        group += 1
    sys.stdout.write(' '.join(map(str, res)))

if __name__ == "__main__":
    main()
