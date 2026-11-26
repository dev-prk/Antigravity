import sys
from collections import Counter

def solve():
    s = sys.stdin.readline().strip()
    q = int(sys.stdin.readline().strip())
    
    n = len(s)
    if n == 0:
        print("Yes")
        return
    
    current = s
    s2_chars = []
    
    for _ in range(q):
        line = sys.stdin.readline().strip()
        if not line:
            continue
        parts = line.split()
        direction = parts[0]
        magnitude = int(parts[1])
        
        mag = magnitude % n
        if mag == 0:
            mag = 0
        
        if direction == 'L':
            current = current[mag:] + current[:mag]
        else:
            current = current[n - mag:] + current[:n - mag]
        
        s2_chars.append(current[0])
    
    s2 = ''.join(s2_chars)
    
    if Counter(s) == Counter(s2):
        print("Yes")
    else:
        print("No")

if __name__ == "__main__":
    solve()
