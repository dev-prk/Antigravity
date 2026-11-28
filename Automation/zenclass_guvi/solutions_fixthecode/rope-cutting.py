import sys
import heapq

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    q = int(next(it))
    ropes = [int(next(it)) for _ in range(n)]

    # Min‑heap of current rope lengths
    heapq.heapify(ropes)

    for _ in range(q):
        if not ropes:
            break
        length = heapq.heappop(ropes)
        if length == 0:
            continue          # shouldn't happen, but safe
        new_len = length // 2    # floor(L/2)
        if new_len > 0:
            heapq.heappush(ropes, new_len)

    print(sum(ropes))

if __name__ == "__main__":
    solve()
