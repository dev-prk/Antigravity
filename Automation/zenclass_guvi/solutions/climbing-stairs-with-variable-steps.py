import sys

def count_ways(n: int) -> int:
    if n < 0:
        return 0
    if n == 0:
        return 1
    # dp[i] only depends on last three values
    a, b, c = 1, 1, 2  # dp[0], dp[1], dp[2]
    if n == 1:
        return b
    if n == 2:
        return c
    for i in range(3, n + 1):
        d = a + b + c
        a, b, c = b, c, d
    return c

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        n = int(data[0])
    except:
        n = 0
    result = count_ways(n)
    sys.stdout.write(str(result))

if __name__ == "__main__":
    main()
