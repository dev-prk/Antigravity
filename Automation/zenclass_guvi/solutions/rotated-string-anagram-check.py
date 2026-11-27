import sys
from collections import Counter

def solve():
    s = sys.stdin.readline().strip()
    if not s:
        print("No")
        return
    
    q_line = sys.stdin.readline().strip()
    if not q_line:
        print("No")
        return
    
    try:
        q = int(q_line)
    except:
        print("No")
        return
    
    s2_chars = []
    current = s
    
    for _ in range(q):
        line = sys.stdin.readline().strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            d = parts[0].upper()
            try:
                r = int(parts[1])
            except:
                continue
            
            n = len(current)
            if d == 'L':
                first_char = current[r % n]
                current = current[r % n:] + current[:r % n]
            else:
                first_char = current[-r % n] if r > 0 else current[0]
                current = current[-r % n:] + current[:-r % n] if r > 0 else current
            
            s2_chars.append(first_char)
    
    s2 = ''.join(s2_chars)
    
    if Counter(s) == Counter(s2):
        print("Yes")
    else:
        print("No")

if __name__ == "__main__":
    solve()
