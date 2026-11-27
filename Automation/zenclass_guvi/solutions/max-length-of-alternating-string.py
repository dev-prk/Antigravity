import sys
from collections import Counter

def solve():
    s = sys.stdin.readline().strip()
    
    if not s:
        print(0)
        return
    
    max_len = 0
    unique_chars = list(set(s))
    
    for i in range(len(unique_chars)):
        for j in range(i + 1, len(unique_chars)):
            c1, c2 = unique_chars[i], unique_chars[j]
            
            filtered = []
            for ch in s:
                if ch == c1 or ch == c2:
                    filtered.append(ch)
            
            if len(filtered) < 2:
                continue
            
            is_alternating = True
            for k in range(len(filtered) - 1):
                if filtered[k] == filtered[k + 1]:
                    is_alternating = False
                    break
            
            if is_alternating:
                max_len = max(max_len, len(filtered))
    
    print(max_len)

if __name__ == "__main__":
    solve()
