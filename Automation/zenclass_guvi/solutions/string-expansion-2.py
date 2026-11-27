import sys
from collections import Counter

def solve():
    s = sys.stdin.readline().strip()
    if not s:
        return
    
    # Extract characters and their counts
    chars = []
    i = 0
    n = len(s)
    while i < n:
        if s[i].isalpha():
            chars.append(s[i])
            i += 1
        else:
            # Collect all consecutive digits
            j = i
            while j < n and s[j].isdigit():
                j += 1
            num = int(s[i:j])
            chars.append(num)
            i = j
    
    # Build the result string
    result = []
    i = 0
    while i < len(chars):
        char = chars[i]
        count = chars[i + 1]
        
        if count % 2 == 0:
            # Expand: char followed by (count-1) copies of char
            result.append(char * count)
        else:
            # Keep as-is: char followed by count
            result.append(char)
            result.append(str(count))
        
        i += 2
    
    sys.stdout.write(''.join(result))

if __name__ == "__main__":
    solve()
