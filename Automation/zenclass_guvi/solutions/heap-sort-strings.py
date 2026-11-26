import sys, heapq

def solve() -> None:
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        n = int(data[0])
    except:
        n = 0
    if n <= 0:
        print()
        return
    strings = data[1:1 + n]
    heapq.heapify(strings)
    sorted_strings = [heapq.heappop(strings) for _ in range(len(strings))]
    sys.stdout.write(' '.join(sorted_strings))

if __name__ == "__main__":
    solve()
