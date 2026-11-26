import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    idx = 0
    try:
        n = int(data[idx])
    except:
        return
    idx += 1
    values = []
    for _ in range(n):
        if idx >= len(data):
            break
        try:
            values.append(int(data[idx]))
        except:
            values.append(data[idx])
        idx += 1
    if idx < len(data):
        try:
            target = int(data[idx])
        except:
            target = data[idx]
    else:
        target = None

    # delete first occurrence of target
    if target is not None:
        for i, v in enumerate(values):
            if v == target:
                del values[i]
                break

    out = " ".join(str(v) for v in values)
    sys.stdout.write(out)

if __name__ == "__main__":
    solve()
