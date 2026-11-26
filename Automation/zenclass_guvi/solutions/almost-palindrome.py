import sys

def is_palindrome(s):
    return s == s[::-1]

def almost_palindrome(s):
    n = len(s)
    left = 0
    right = n - 1
    
    while left < right:
        if s[left] != s[right]:
            # Try removing left character or right character
            skip_left = s[left + 1:right + 1]
            skip_right = s[left:right]
            return is_palindrome(skip_left) or is_palindrome(skip_right)
        left += 1
        right -= 1
    
    return True  # Already a palindrome

def main():
    s = sys.stdin.readline().strip()
    if almost_palindrome(s):
        print("YES")
    else:
        print("NO")

if __name__ == "__main__":
    main()
