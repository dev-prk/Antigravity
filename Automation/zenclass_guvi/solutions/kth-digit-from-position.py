import sys

def solve():
    data = sys.stdin.read().strip().split()
    if len(data) < 3:
        return
    # take first three values
    N_str, P_str, K_str = data[0], data[1], data[2]
    try:
        N = int(N_str)
    except:
        # if not a valid int, treat as 0
        N = 0
    try:
        P = int(P_str)
        K = int(K_str)
    except:
        print(-1)
        return

    s = str(abs(N))          # work with absolute value, ignore sign
    idx = P + K - 1          # 0‑based index of the required digit

    if 0 <= idx < len(s):
        sys.stdout.write(s[idx])
    else:
        sys.stdout.write("-1")

if __name__ == "__main__":
    solve()
