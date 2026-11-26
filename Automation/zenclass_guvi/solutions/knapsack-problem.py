import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print(0)
        return
    
    weights = list(map(int, data[2:2+n]))
    prices = list(map(int, data[2+n:2+2*n]))
    
    dp = [0] * (m + 1)
    
    for i in range(n):
        w = weights[i]
        p = prices[i]
        for wt in range(m, w - 1, -1):
            dp[wt] = max(dp[wt], dp[wt - w] + p)
    
    print(dp[m])

if __name__ == "__main__":
    main()
