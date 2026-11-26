import sys

def longest_palindromic_substring(s):
    if not s:
        return 0
    
    n = len(s)
    start = 0
    max_length = 1
    
    for i in range(n):
        # Check for odd length palindromes with center at i
        left = i - 1
        right = i + 1
        while left >= 0 and right < n and s[left] == s[right]:
            if right - left + 1 > max_length:
                max_length = right - left + 1
                start = left
            left -= 1
            right += 1
        
        # Check for even length palindromes with center between i and i+1
        left = i
        right = i + 1
        while left >= 0 and right < n and s[left] == s[right]:
            if right - left + 1 > max_length:
                max_length = right - left + 1
                start = left
            left -= 1
            right += 1
    
    return max_length

def main():
    s = sys.stdin.readline().strip()
    result = longest_palindromic_substring(s)
    print(result)

if __name__ == "__main__":
    main()
