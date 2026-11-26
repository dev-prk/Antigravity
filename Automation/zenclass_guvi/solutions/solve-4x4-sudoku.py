import sys


def is_valid(grid, row, col, num):
    # Check row
    if num in grid[row]:
        return False
    # Check column
    for i in range(4):
        if grid[i][col] == num:
            return False
    # Check 2x2 subgrid
    start_row = (row // 2) * 2
    start_col = (col // 2) * 2
    for i in range(start_row, start_row + 2):
        for j in range(start_col, start_col + 2):
            if grid[i][j] == num:
                return False
    return True


def solve(grid):
    for i in range(4):
        for j in range(4):
            if grid[i][j] == 0:
                for num in range(1, 5):
                    if is_valid(grid, i, j, num):
                        grid[i][j] = num
                        if solve(grid):
                            return True
                        grid[i][j] = 0
                return False
    return True


def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    grid = []
    idx = 0
    for _ in range(4):
        row = []
        for _ in range(4):
            row.append(int(data[idx]))
            idx += 1
        grid.append(row)

    solve(grid)

    for row in grid:
        print(' '.join(map(str, row)))


if __name__ == '__main__':
    main()
