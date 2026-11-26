import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        print("NO")
        return
    
    m = int(data[0])
    n = int(data[1])
    
    if m == 0 or n == 0:
        print("NO")
        return
    
    matrix = []
    idx = 2
    for i in range(m):
        row = list(map(int, data[idx:idx+n]))
        matrix.append(row)
        idx += n
    
    # Check for downward-pointing triangle
    # For triangle with base n (n must be odd)
    def check_downward_triangle(mat, rows, cols):
        if rows * 2 - 1 > cols:
            return False
        for i in range(min(rows, len(mat))):
            width = 2 * i + 1
            if width > cols:
                return False
            center = (width - 1) // 2
            start_col = (cols - width) // 2
            end_col = start_col + width - 1
            for j in range(start_col, end_col + 1):
                if j >= len(mat[i]) or mat[i][j] != 7:
                    return False
        return True
    
    # Check for upward-pointing triangle
    def check_upward_triangle(mat, rows, cols):
        if rows * 2 - 1 > cols:
            return False
        base_width = 2 * rows - 1
        if base_width > cols:
            return False
        for i in range(rows):
            width = base_width - 2 * i
            start_col = (cols - width) // 2
            end_col = start_col + width - 1
            for j in range(start_col, end_col + 1):
                if j >= len(mat[i]) or mat[i][j] != 7:
                    return False
        return True
    
    # Try all possible triangle sizes
    for size in range(1, min(m, n) + 1):
        if check_downward_triangle(matrix, size, n):
            print("YES")
            return
        if check_upward_triangle(matrix, size, n):
            print("YES")
            return
    
    print("NO")

solve()
