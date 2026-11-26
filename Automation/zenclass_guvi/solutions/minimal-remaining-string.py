import sys

def minimal_remaining_string(s):
    n = len(s)
    if n == 0:
        return ""
    
    max_len = 0
    for l in range(1, n // 2 + 1):
        prefix_rev = s[:l][::-1]
        suffix = s[n-l:]
        if prefix_rev == suffix:
            max_len = l
        else:
            break
    
    return s[max_len:n-max_len]

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = minimal_remaining_string(s)
    
    if not result:
        print("Minimal string is empty")
    else:
        print(result)

if __name__ == "__main__":
    main()
