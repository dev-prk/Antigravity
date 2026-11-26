import sys

def min_swaps(arr):
    n = len(arr)
    if n <= 1:
        return 0
    # pair each element with its original index
    paired = [(val, idx) for idx, val in enumerate(arr)]
    # sort by value
    paired.sort(key=lambda x: x[0])
    # position where each original index should go
    pos = [0] * n
    for sorted_idx, (_, orig_idx) in enumerate(paired):
        pos[orig_idx] = sorted_idx

    visited = [False] * n
    swaps = 0

    for i in range(n):
        if visited[i] or pos[i] == i:
            continue
        cycle_len = 0
        j = i
        while not visited[j]:
            visited[j] = True
            j = pos[j]
            cycle_len += 1
        swaps += cycle_len - 1
    return swaps

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    heights = list(map(int, data[1:1 + n])) if n > 0 else []
    print(min_swaps(heights))

if __name__ == "__main__":
    main()
