from collections import Counter

def solve():
    s = input().strip()
    
    if not s:
        print(-1)
        return
    
    count = Counter(s)
    
    for char in s:
        if count[char] == 1:
            print(char)
            return
    
    print(-1)

if __name__ == "__main__":
    solve()
