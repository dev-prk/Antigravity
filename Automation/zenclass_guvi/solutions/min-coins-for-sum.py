import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    s = int(data[1])
    
    if n == 0 or s < 0:
        print(-1)
        return
    
    coins = list(map(int, data[2:2+n]))
    
    if s == 0:
        print(0)
        return
    
    coins = [c for c in coins if c > 0 and c <= s]
    
    if not coins:
        print(-1)
        return
    
    dp = [float('inf')] * (s + 1)
    dp[0] = 0
    
    for i in range(1, s + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    if dp[s] == float('inf'):
        print(-1)
    else:
        print(dp[s])

if __name__ == "__main__":
    main()
