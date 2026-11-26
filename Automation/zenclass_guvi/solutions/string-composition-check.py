def can_form_string(s):
    n = len(s)
    if n == 0:
        return 0
    
    # dp[i] = True if s[0:i] can be formed
    dp = [False] * (n + 1)
    dp[0] = True
    
    for i in range(1, n + 1):
        # Check if current char is 'A' (single A)
        if s[i-1] == 'A':
            dp[i] = dp[i-1]
        
        # Check for AB (2 chars ending at i)
        if i >= 2 and dp[i-2] and s[i-2] == 'A' and s[i-1] == 'B':
            dp[i] = True
        
        # Check for ABB (3 chars ending at i)
        if i >= 3 and dp[i-3] and s[i-3] == 'A' and s[i-2] == 'B' and s[i-1] == 'B':
            dp[i] = True
    
    return 1 if dp[n] else 0

s = input().strip()
print(can_form_string(s))
