import sys

def solve():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        print(-1)
        return
    
    s1 = data[0]
    s2 = data[1]
    
    chars_to_remove = set(s2)
    result = [char for char in s1 if char not in chars_to_remove]
    
    if not result:
        print(-1)
    else:
        print(''.join(result))

if __name__ == "__main__":
    solve()
