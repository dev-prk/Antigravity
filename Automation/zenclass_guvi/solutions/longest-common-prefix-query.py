import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    strings = []
    for _ in range(N):
        strings.append(data[idx])
        idx += 1
    
    Q = int(data[idx])
    idx += 1
    
    queries = []
    for _ in range(Q):
        parts = data[idx].split()
        M = int(parts[0])
        X = int(parts[1])
        queries.append((M, X))
        idx += 1
    
    min_prefix = [0] * (N + 1)
    if N > 0:
        min_prefix[1] = len(strings[0])
    
    for i in range(2, N + 1):
        s1 = strings[i - 2]
        s2 = strings[i - 1]
        common_len = 0
        for j in range(min(len(s1), len(s2))):
            if s1[j] == s2[j]:
                common_len += 1
            else:
                break
        min_prefix[i] = min(min_prefix[i - 1], common_len)
    
    for M, X in queries:
        if min_prefix[M] >= X:
            print("YES")
        else:
            print("NO")

if __name__ == "__main__":
    main()
