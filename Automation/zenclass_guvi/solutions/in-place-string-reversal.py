import sys

def main():
    s = list(sys.stdin.read())
    # Remove trailing newline if present
    if s and s[-1] == '\n':
        s.pop()
    
    left = 0
    right = len(s) - 1
    
    while left < right:
        if not s[left].isalnum():
            left += 1
        elif not s[right].isalnum():
            right -= 1
        else:
            s[left], s[right] = s[right], s[left]
            left += 1
            right -= 1
    
    print(''.join(s))

if __name__ == "__main__":
    main()
