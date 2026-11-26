import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    seen = set()
    res = []
    for x in arr:
        if x not in seen:
            seen.add(x)
            res.append(x)
    print(' '.join(map(str, res)))

if __name__ == "__main__":
    main()
