import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    parts = data.split()
    if len(parts) < 2:
        return
    s = parts[0]
    try:
        k = int(parts[1])
    except ValueError:
        return
    if k <= 0:
        return
    res = []
    for i in range(k - 1, len(s), k):
        res.append(s[i])
    print(' '.join(res))

if __name__ == "__main__":
    main()
