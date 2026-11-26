import sys

def count_vowels(s):
    """Count the number of vowels in a string (case-insensitive)."""
    vowels = set('aeiouAEIOU')
    return sum(1 for char in s if char in vowels)

def solve():
    """Read input, sort strings by vowel count, and print result."""
    # Read N
    line = sys.stdin.readline()
    if not line:
        return
    n = int(line.strip())
    
    # Read N strings
    strings = []
    for _ in range(n):
        s = sys.stdin.readline().rstrip('\n')
        strings.append(s)
    
    # Sort by vowel count in descending order
    # If vowel counts are equal, maintain original order (stable sort)
    strings.sort(key=lambda x: count_vowels(x), reverse=True)
    
    # Print result
    for s in strings:
        print(s)

if __name__ == "__main__":
    solve()
