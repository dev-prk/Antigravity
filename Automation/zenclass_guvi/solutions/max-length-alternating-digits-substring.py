import sys

def solve():
    s = sys.stdin.readline().strip()
    if not s:
        print(0)
        return
    
    max_len = 1
    curr_len = 1
    
    for i in range(1, len(s)):
        prev_digit = int(s[i-1])
        curr_digit = int(s[i])
        
        if (prev_digit % 2) != (curr_digit % 2):
            curr_len += 1
            max_len = max(max_len, curr_len)
        else:
            curr_len = 1
    
    print(max_len)

if __name__ == "__main__":
    solve()
