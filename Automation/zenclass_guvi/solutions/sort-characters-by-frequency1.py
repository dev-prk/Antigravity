from collections import Counter

def solve():
    s = input().strip()
    if not s:
        print("")
        return
    
    freq = Counter(s)
    sorted_chars = sorted(freq.keys(), key=lambda c: (-freq[c], c))
    result = ''.join(c * freq[c] for c in sorted_chars)
    print(result)

solve()
