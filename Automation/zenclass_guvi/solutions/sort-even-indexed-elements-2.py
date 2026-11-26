import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    even_vals = [arr[i] for i in range(0, n, 2)]
    even_vals.sort()
    res = arr[:]  # copy
    for i, val in zip(range(0, n, 2), even_vals):
        res[i] = val
    print(' '.join(map(str, res)))

if __name__ == "__main__":
    main()
