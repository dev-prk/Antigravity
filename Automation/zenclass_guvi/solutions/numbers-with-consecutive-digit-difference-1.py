import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    
    result = []
    for num in range(1, n + 1):
        s = str(num)
        valid = True
        for i in range(len(s) - 1):
            if abs(int(s[i]) - int(s[i + 1])) != 1:
                valid = False
                break
        if valid and len(s) >= 2:
            result.append(str(num))
    
    if not result:
        print("-1")
    else:
        print(" ".join(result))

solve()
