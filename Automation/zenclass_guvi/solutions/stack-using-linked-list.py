import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    idx = 0
    N = int(data[idx]); idx += 1

    stack = []
    for _ in range(N):
        if idx >= len(data):
            break
        stack.append(int(data[idx]))
        idx += 1

    if idx < len(data):
        op = int(data[idx]); idx += 1
        if op == 1:          # push
            if idx < len(data):
                val = int(data[idx]); idx += 1
                stack.append(val)
        elif op == 2:        # pop
            if stack:
                stack.pop()

    sys.stdout.write(' '.join(map(str, stack)))

if __name__ == "__main__":
    solve()
