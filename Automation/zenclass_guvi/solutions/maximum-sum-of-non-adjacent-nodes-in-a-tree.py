import sys

def solve() -> None:
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    if n == 0:
        print(0)
        return
    vals = [0] + [int(next(it)) for _ in range(n)]
    adj = [[] for _ in range(n + 1)]
    for _ in range(n - 1):
        u = int(next(it)); v = int(next(it))
        adj[u].append(v)
        adj[v].append(u)

    sys.setrecursionlimit(1_000_000)

    include = [0] * (n + 1)
    exclude = [0] * (n + 1)

    stack = [(1, 0, 0)]  # node, parent, state 0=pre,1=post
    while stack:
        node, parent, state = stack.pop()
        if state == 0:
            stack.append((node, parent, 1))
            for nb in adj[node]:
                if nb != parent:
                    stack.append((nb, node, 0))
        else:
            inc = vals[node]
            exc = 0
            for nb in adj[node]:
                if nb == parent:
                    continue
                inc += exclude[nb]
                exc += max(include[nb], exclude[nb])
            include[node] = inc
            exclude[node] = exc

    result = max(include[1], exclude[1])
    print(result)

if __name__ == "__main__":
    solve()
