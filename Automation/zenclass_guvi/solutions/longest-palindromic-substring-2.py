import sys

def longest_palindromic_substring(s):
    n = len(s)
    if n == 0:
        return ""
    
    start = 0
    max_len = 1
    
    for i in range(n):
        # Check for odd length palindromes with center at i
        l, r = i, i
        while l >= 0 and r < n and s[l] == s[r]:
            if r - l + 1 > max_len:
                max_len = r - l + 1
                start = l
            l -= 1
            r += 1
        
        # Check for even length palindromes with center between i and i+1
        l, r = i, i + 1
        while l >= 0 and r < n and s[l] == s[r]:
            if r - l + 1 > max_len:
                max_len = r - l + 1
                start = l
            l -= 1
            r += 1
    
    return s[start:start + max_len]

def main():
    s = sys.stdin.readline().strip()
    result = longest_palindromic_substring(s)
    print(result)

if __name__ == "__main__":
    main()
