import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    arr = list(map(int, data[2:2+n])) if len(data) > 2 else []
    
    total_subarrays = n * (n + 1) // 2
    count_max_le_k = 0
    cur_len = 0
    
    for x in arr:
        if x <= k:
            cur_len += 1
        else:
            count_max_le_k += cur_len * (cur_len + 1) // 2
            cur_len = 0
    count_max_le_k += cur_len * (cur_len + 1) // 2  # trailing segment
    
    ans = total_subarrays - count_max_le_k
    print(ans)

if __name__ == "__main__":
    solve()
