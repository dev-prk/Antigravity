import sys

def solve() -> None:
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    try:
        q = int(data[0].strip())
    except:
        return
    outputs = []
    min_val = None  # current minimum
    idx = 1
    for _ in range(q):
        if idx >= len(data):
            break
        parts = data[idx].strip().split()
        idx += 1
        if not parts:
            continue
        if parts[0] == '1' and len(parts) >= 2:
            try:
                val = int(parts[1])
            except:
                continue
            if min_val is None or val < min_val:
                min_val = val
        elif parts[0] == '2':
            outputs.append(str(min_val) if min_val is not None else "-1")
        # ignore any malformed lines
    sys.stdout.write(" ".join(outputs))

if __name__ == "__main__":
    solve()
