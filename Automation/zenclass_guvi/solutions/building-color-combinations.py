import sys

MOD = 1000000007

def main():
    line = sys.stdin.readline()
    if not line:
        return
    N = line.strip()
    if not N:
        return
    N = int(N)
    
    if N <= 0:
        print(0)
        return
    if N == 1:
        print(2)
        return
    
    # dp[i] = number of ways to build i buildings where last building is blue
    # ep[i] = number of ways to build i buildings where last building is red
    
    prev_dp = 1  # dp[1] = 1 (build 1st as blue)
    prev_ep = 1  # ep[1] = 1 (build 1st as red)
    
    for i in range(2, N + 1):
        # dp[i] = dp[i-1] + ep[i-1] (can place blue after any configuration)
        curr_dp = (prev_dp + prev_ep) % MOD
        
        # ep[i] = dp[i-1] (can place red only after blue)
        # Note: prev_ep doesn't contribute because placing red after red violates the rule
        # Actually, let me reconsider...
        # If we place red at position i, then position i-1 must be blue
        # So ep[i] = dp[i-1]
        curr_ep = prev_dp
        
        prev_dp = curr_dp
        prev_ep = curr_ep
    
    ans = (prev_dp + prev_ep) % MOD
    print(ans)

if __name__ == "__main__":
    main()
