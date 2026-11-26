import sys
from collections import Counter

def can_form_palindrome_with_one_change(s):
    if not s:
        return "YES"
    
    freq = Counter(s)
    odd_count = sum(1 for count in freq.values() if count % 2 == 1)
    
    # If already a palindrome permutation, check if we can change one char
    # Actually, if odd_count <= 1, we can already form palindrome
    if odd_count <= 1:
        return "YES"
    
    # We need to reduce odd_count by at most 2 (by changing one character)
    # So if odd_count <= 3, we can do it
    if odd_count <= 3:
        return "YES"
    
    return "NO"

def main():
    s = sys.stdin.readline().strip()
    result = can_form_palindrome_with_one_change(s)
    print(result)

if __name__ == "__main__":
    main()
