import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    r = int(data[0])
    c = int(data[1])
    idx = 2
    matrix = []
    for _ in range(r):
        row = list(map(int, data[idx:idx+c]))
        matrix.append(row)
        idx += c

    row_sums = [sum(row) for row in matrix]
    col_sums = [0] * c
    for row in matrix:
        for j in range(c):
            col_sums[j] += row[j]

    print(f"[{', '.join(map(str, row_sums))}]")
    print(f"[{', '.join(map(str, col_sums))}]")

if __name__ == "__main__":
    solve()
