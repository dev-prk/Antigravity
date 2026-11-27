import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        print(-1)
        return
    
    # Parse input like "p=[2,3,1],k=1"
    # Find p=[...] part
    if 'p=[' not in data:
        print(-1)
        return
    
    start = data.index('p=[') + 3
    end = data.index(']', start)
    p_str = data[start:end]
    p = [int(x) for x in p_str.split(',')]
    
    if ',k=' in data:
        k_start = data.index(',k=', end) + 3
        k_end = data.index(',', k_start) if ',' in data[k_start:] else len(data)
        k_str = data[k_start:k_end]
        k = int(k_str)
    else:
        print(-1)
        return
    
    if not p or k < 0:
        print(-1)
        return
    
    n = len(p)
    
    # Convert to 0-indexed
    perm = [x - 1 for x in p]
    
    # Handle k=0 case (identity)
    if k == 0:
        result = list(range(1, n + 1))
        print('[' + ','.join(map(str, result)) + ']')
        return
    
    # Binary lifting
    LOG = 60  # Since k can be up to 1e18
    
    # dp[i][j] = permutation after 2^i applications starting from j
    dp = [[0] * n for _ in range(LOG)]
    
    # Base case: 2^0 = 1 step
    for j in range(n):
        dp[0][j] = perm[j]
    
    # Build the table
    for i in range(1, LOG):
        for j in range(n):
            dp[i][j] = dp[i-1][dp[i-1][j]]
    
    # Apply k steps to each position
    result = [0] * n
    for start in range(n):
        pos = start
        remaining = k
        for i in range(LOG - 1, -1, -1):
            if remaining >= (1 << i):
                pos = dp[i][pos]
                remaining -= (1 << i)
        result[pos] = start + 1  # Convert back to 1-indexed
    
    print('[' + ','.join(map(str, result)) + ']')

if __name__ == "__main__":
    main()
