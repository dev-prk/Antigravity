import sys

def solve() -> None:
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    it = iter(data)
    N = int(next(it))
    targets = [int(next(it)) for _ in range(N)]
    Q = int(next(it))

    # segment tree (iterative) for range maximum
    size = 1
    while size < N:
        size <<= 1
    seg = [0] * (2 * size)
    heights = [0] * N

    def seg_update(idx: int, value: int) -> None:
        pos = idx + size
        seg[pos] = value
        pos >>= 1
        while pos:
            seg[pos] = seg[pos << 1] if seg[pos << 1] >= seg[(pos << 1) | 1] else seg[(pos << 1) | 1]
            pos >>= 1

    def seg_query(l: int, r: int) -> int:
        if l > r:
            l, r = r, l
        l += size
        r += size
        res = 0
        while l <= r:
            if l & 1:
                if seg[l] > res:
                    res = seg[l]
                l += 1
            if not (r & 1):
                if seg[r] > res:
                    res = seg[r]
                r -= 1
            l >>= 1
            r >>= 1
        return res

    out_lines = []
    for _ in range(Q):
        typ = int(next(it))
        x = int(next(it))
        y = int(next(it))
        if typ == 1:
            idx = x - 1
            if 0 <= idx < N:
                new_h = heights[idx] + y
                cap = targets[idx]
                if new_h > cap:
                    new_h = cap
                if new_h != heights[idx]:
                    heights[idx] = new_h
                    seg_update(idx, new_h)
        else:  # typ == 2
            l = x - 1
            r = y - 1
            if N == 0:
                out_lines.append('0')
            else:
                out_lines.append(str(seg_query(l, r)))
    sys.stdout.write('\n'.join(out_lines))

if __name__ == "__main__":
    solve()
