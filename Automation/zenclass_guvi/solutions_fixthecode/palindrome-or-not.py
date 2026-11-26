def can_be_palindrome(s):
    n = len(s)
    if n <= 1:
        return True
    
    left, right = 0, n - 1
    
    while left < right:
        if s[left] == s[right]:
            left += 1
            right -= 1
        else:
            # Try removing left character or right character
            skip_left = s[left + 1:right + 1]
            skip_right = s[left:right]
            return skip_left == skip_left[::-1] or skip_right == skip_right[::-1]
    
    return True

s = input().strip()
result = can_be_palindrome(s)
print("YES" if result else "NO")
