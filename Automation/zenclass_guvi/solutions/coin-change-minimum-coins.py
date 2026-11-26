import sys

def solve() -> None:
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    amount = int(data[1])
    coins = []
    idx = 2
    for _ in range(n):
        if idx < len(data):
            coins.append(int(data[idx]))
            idx += 1

    # Keep only positive denominations to avoid invalid coin values.
    coins = [c for c in coins if c > 0]

    INF = amount + 1
    dp = [INF] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        best = INF
        for c in coins:
            if c <= i:
                cand = dp[i - c] + 1
                if cand < best:
                    best = cand
        dp[i] = best

    ans = dp[amount]
    print(-1 if ans >= INF else ans)

if __name__ == "__main__":
    solve()
