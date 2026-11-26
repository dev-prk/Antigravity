import sys
from collections import Counter

def solve():
    s = sys.stdin.readline().strip()
    if not s:
        return
    
    # Handle unique characters
    freq = Counter(s)
    unique_chars = sorted(freq.keys())
    
    # Use iterative backtracking with heap allocation
    n = len(s)
    result = []
    
    def backtrack(path, counter):
        if len(path) == n:
            result.append(''.join(path))
            return
        
        for c in unique_chars:
            if counter[c] > 0:
                counter[c] -= 1
                path.append(c)
                backtrack(path, counter)
                path.pop()
                counter[c] += 1
    
    backtrack([], freq.copy())
    sys.stdout.write('\n'.join(result))

solve()
