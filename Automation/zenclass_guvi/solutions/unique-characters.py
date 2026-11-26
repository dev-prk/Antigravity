from collections import Counter
import sys

# Read input
s = sys.stdin.read().strip()

if not s:
    print(-1)
else:
    # Count frequency of each character
    freq = Counter(s)
    
    # Find characters that appear exactly once, in order of appearance
    unique_chars = []
    for char in s:
        if freq[char] == 1:
            unique_chars.append(char)
    
    # Print result
    if unique_chars:
        print(' '.join(unique_chars))
    else:
        print(-1)
