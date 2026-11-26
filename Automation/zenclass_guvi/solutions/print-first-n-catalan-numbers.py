import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n < 0:
        return

    cats = [1]
    for i in range(n):
        cats.append(cats[-1] * 2 * (2 * i + 1) // (i + 2))

    sys.stdout.write(" ".join(map(str, cats)))

if __name__ == "__main__":
    main()
