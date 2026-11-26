import sys

def solve() -> None:
    data = list(map(int, sys.stdin.read().strip().split()))
    if not data:
        return
    N, W = data[0], data[1]
    if N <= 0 or W <= 0:
        print(0)
        return
    weights = data[2:2 + N]
    values = data[2 + N:2 + 2 * N]

    zero_val_sum = 0
    items = []
    for wt, val in zip(weights, values):
        if wt == 0:
            zero_val_sum += val
        elif wt > 0:
            items.append((wt, val))
        # ignore negative weights

    dp = [0] * (W + 1)
    for wt, val in items:
        if wt > W:
            continue
        for w in range(W, wt - 1, -1):
            new_val = dp[w - wt] + val
            if new_val > dp[w]:
                dp[w] = new_val

    print(zero_val_sum + dp[W])

if __name__ == "__main__":
    solve()
