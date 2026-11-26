import sys

def longest_substring_without_repeating(s):
    seen = {}
    max_length = 0
    start = 0
    
    for i in range(len(s)):
        if s[i] in seen and seen[s[i]] >= start:
            start = seen[s[i]] + 1
        seen[s[i]] = i
        max_length = max(max_length, i - start + 1)
    
    return max_length

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print(0)
        return
    print(longest_substring_without_repeating(s))

if __name__ == "__main__":
    main()
