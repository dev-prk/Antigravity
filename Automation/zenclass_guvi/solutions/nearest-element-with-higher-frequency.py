import sys
from collections import Counter

def solve():
    n = int(sys.stdin.readline().strip())
    arr = list(map(int, sys.stdin.readline().split()))
    
    if n == 0:
        print("")
        return
    
    freq = Counter(arr)
    result = [-1] * n
    
    for i in range(n - 2, -1, -1):
        current_freq = freq[arr[i]]
        j = i + 1
        
        while j < n:
            if freq[arr[j]] > current_freq:
                result[i] = arr[j]
                break
            j += 1
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    solve()
