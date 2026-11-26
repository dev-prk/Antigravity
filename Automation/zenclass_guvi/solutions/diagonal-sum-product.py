import sys

def main():
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    it = iter(data)
    n = next(it)
    sum_main = 0
    sum_anti = 0
    for i in range(n):
        row = [next(it) for _ in range(n)]
        sum_main += row[i]
        sum_anti += row[n - 1 - i]
    print(sum_main * sum_anti)

if __name__ == "__main__":
    main()
