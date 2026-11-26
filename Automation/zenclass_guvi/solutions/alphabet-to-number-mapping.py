import sys

def count_decodings(s: str) -> int:
    if not s or s[0] == '-':
        return 0
    n = len(s)
    # dp_prev2 = dp[i-2], dp_prev1 = dp[i-1]
    dp_prev2 = 1
    dp_prev1 = 0 if s[0] == '0' else 1

    for i in range(1, n):
        cur = 0
        if s[i] != '0':
            cur += dp_prev1
        two = (s[i-1] == '1') or (s[i-1] == '2' and s[i] <= '6')
        if two:
            cur += dp_prev2
        dp_prev2, dp_prev1 = dp_prev1, cur
        if dp_prev1 == 0 and s[i] == '0' and not two:
            # early exit: impossible decoding
            return 0
    return dp_prev1

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    # In case of multiple lines/spaces, take first token that looks like a number
    token = data.split()[0]
    result = count_decodings(token)
    sys.stdout.write(str(result))

if __name__ == "__main__":
    main()
