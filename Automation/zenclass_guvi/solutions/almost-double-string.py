import sys

def solve():
    s = sys.stdin.readline().strip()
    n = len(s)
    
    if n == 0:
        print("NO")
        return
    
    # Try removing each position
    for i in range(n):
        # Remove character at position i
        t = s[:i] + s[i+1:]
        
        m = len(t)
        half = m // 2
        
        # Check if first half equals second half
        if t[:half] == t[half:]:
            print("YES")
            return
    
    print("NO")

if __name__ == "__main__":
    solve()
