import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print(0)
        return
    n, _ = map(int, data[0].split())
    total = 0.0
    for i in range(n):
        row = list(map(float, data[1 + i].split()))
        for j in range(i, n):
            total += row[j]
    print(int(round(total * 1000)))

if __name__ == "__main__":
    main()
