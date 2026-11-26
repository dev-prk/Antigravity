import sys

def longest_increasing_streak(prices):
    """Find the longest increasing consecutive streak."""
    if not prices:
        return 0
    
    max_streak = 1
    current_streak = 1
    
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
    
    return max_streak

def next_greater_elements(prices):
    """Find next greater element for each day using stack."""
    n = len(prices)
    nge = [-1] * n
    stack = []
    
    for i in range(n-1, -1, -1):
        while stack and prices[i] >= stack[-1]:
            stack.pop()
        
        if stack:
            nge[i] = stack[-1]
        
        stack.append(prices[i])
    
    return nge

def max_profit_k_transactions(prices, k):
    """Compute maximum profit with at most k transactions."""
    if not prices or len(prices) < 2 or k == 0:
        return 0
    
    # If k >= n//2, we can make at most n//2 transactions
    # which is equivalent to unlimited transactions
    if k >= len(prices) // 2:
        profit = 0
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                profit += prices[i] - prices[i-1]
        return profit
    
    # DP approach for limited transactions
    # dp[i][j] = max profit using j transactions up to day i
    # We can optimize space by using 1D arrays
    
    prev = [0] * len(prices)
    curr = [0] * len(prices)
    
    for t in range(1, k + 1):
        # Track max(prev[j-1] - prices[j]) for all j < i
        max_diff = prev[0] - prices[0]
        curr[0] = 0
        
        for i in range(1, len(prices)):
            # Either don't trade on day i, or buy at some day j < i and sell at i
            curr[i] = max(curr[i-1], prices[i] + max_diff)
            max_diff = max(max_diff, prev[i] - prices[i])
        
        prev, curr = curr, prev
    
    return prev[-1]

def main():
    # Read input
    n = int(sys.stdin.readline().strip())
    prices = list(map(int, sys.stdin.readline().strip().split()))
    k = int(sys.stdin.readline().strip())
    
    # Solve problems
    longest_streak = longest_increasing_streak(prices)
    max_profit = max_profit_k_transactions(prices, k)
    
    # Print output
    print(f"Longest Increasing Streak: {longest_streak}")
    print(f"Max Profit: {max_profit}")

if __name__ == "__main__":
    main()
