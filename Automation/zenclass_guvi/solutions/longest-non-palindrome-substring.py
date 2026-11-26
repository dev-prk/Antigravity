import sys

def is_palindrome(s):
    return s == s[::-1]

def solve():
    s = sys.stdin.readline().rstrip('\n')
    n = len(s)
    
    if n == 0:
        print("")
        return
    
    # Check if entire string is not a palindrome
    if not is_palindrome(s):
        print(s)
        return
    
    # Try removing one character from the end (left to right elimination)
    for i in range(n - 1, -1, -1):
        substr = s[:i] + s[i+1:]
        if substr and not is_palindrome(substr):
            print(substr)
            return
    
    # All single removals result in palindromes, check length n-2
    for i in range(n - 1, -1, -1):
        substr = s[:i] + s[i+1:]
        if substr and not is_palindrome(substr):
            print(substr)
            return
    
    # If all substrings of length n-1 are palindromes
    # The answer is the first character (or any single char that's not equal to itself)
    # Since single char is always palindrome, we need to find non-palindrome
    # But single char is always palindrome, so if all n-1 substrings are palindromes
    # then the only non-palindrome substrings are of length < n-1
    # Actually, if string has all same chars, then any substr is palindrome
    # In that case, there's NO non-palindrome substring!
    # But problem says print max length non-palindrome
    # If all chars same, any proper substr is palindrome
    
    # Find the longest non-palindrome substring
    # If entire string is palindrome, check n-1
    # If all n-1 length substrings are palindromes, check n-2, etc.
    
    for length in range(n - 1, 0, -1):
        for start in range(n - length + 1):
            substr = s[start:start + length]
            if not is_palindrome(substr):
                # Find the one obtained by elimination at end
                best_substr = substr
                for i in range(n - 1, -1, -1):
                    test_substr = s[:i] + s[i+1:]
                    if len(test_substr) == length and not is_palindrome(test_substr):
                        best_substr = test_substr
                        break
                print(best_substr)
                return
    
    print("")

if __name__ == "__main__":
    solve()
