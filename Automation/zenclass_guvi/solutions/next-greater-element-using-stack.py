import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    arr = [int(next(it)) for _ in range(n)]
    m = int(next(it))
    queries = [int(next(it)) for _ in range(m)]
    
    nge = [-1] * n
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and stack[-1] <= arr[i]:
            stack.pop()
        if stack:
            nge[i] = stack[-1]
        stack.append(arr[i])
    
    out = [str(nge[q]) for q in queries]
    print(' '.join(out))

if __name__ == '__main__':
    solve()
