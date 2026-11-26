import sys

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print(0)
        return
    
    n = len(s)
    min_k = n
    
    for c in set(s):
        prev_pos = -1
        max_gap = 0
        
        for i in range(n):
            if s[i] == c:
                gap = i - prev_pos
                max_gap = max(max_gap, gap)
                prev_pos = i
        
        # Check gap from last occurrence to end
        gap = n - prev_pos
        max_gap = max(max_gap, gap)
        
        # The k-dominant value for character c is the maximum gap
        min_k = min(min_k, max_gap)
    
    print(min_k)

if __name__ == "__main__":
    main()
