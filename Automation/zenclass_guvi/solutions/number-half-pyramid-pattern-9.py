import sys

def solve():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    
    # Total numbers used: R*(R+1)/2
    total = R * (R + 1) // 2
    
    # We'll create a 2D grid
    grid = [[0] * (R + 1) for _ in range(R + 1)]  # 1-indexed
    
    # Counter
    cnt = 1
    
    # Column 1: 1 to R (top to bottom)
    for r in range(R):
        grid[r + 1][1] = cnt
        cnt += 1
    
    # Now for columns 2 to R
    # Each column has R - col + 1 elements
    # Direction alternates: col2 upwards, col3 downwards, col4 upwards, ...
    # For R=5:
    #   col1: 1,2,3,4,5 (top to bottom)
    #   col2: upwards -> 9,8,7,6 (top to bottom) means top is 9, bottom is 6
    #   col3: downwards -> 10,11,12 (top to bottom) means top is 10, bottom is 12
    #   col4: upwards -> 14,13 (top to bottom) means top is 14, bottom is 13
    #   col5: 15
    
    # Let's think about the order of filling
    # After col1 (5 numbers), cnt = 6
    # Col2 has 4 numbers: 6,7,8,9. Upwards means values increase from bottom to top.
    # So bottom (row 2) gets 6, row 1 gets 9? Wait, let's look at sample.
    # Row 1: col1=1
    # Row 2: col1=2, col2=9
    # Row 3: col1=3, col2=8, col3=10
    # Row 4: col1=4, col2=7, col3=11, col4=14
    # Row 5: col1=5, col2=6, col3=12, col4=13, col5=15
    
    # Col2 values top to bottom: 9,8,7,6. These are 9,8,7,6. The numbers used are 6,7,8,9.
    # Col3 values top to bottom: 10,11,12. Numbers used are 10,11,12.
    # Col4 values top to bottom: 14,13. Numbers used are 13,14.
    # Col5 values top to bottom: 15. Numbers used are 15.
    
    # So for each column c (starting from 2):
    # Number of elements in this column = R - c + 1
    # The numbers to use are the next 'num_elements' numbers starting from cnt.
    # If direction is "upwards" (values decrease top to bottom, or increase bottom to top):
    #   the first number in sequence goes to the bottom row of that column.
    # If direction is "downwards" (values increase top to bottom):
    #   the first number in sequence goes to the top row of that column.
    
    # Direction pattern: col2 upwards, col3 downwards, col4 upwards, etc.
    # So for column c: if (c % 2 == 0), it's upwards; else downwards.
    
    for c in range(2, R + 1):
        num_elements = R - c + 1
        is_upwards = (c % 2 == 0)
        
        # Save the starting value
        start_val = cnt
        
        if is_upwards:
            # Fill from bottom row to top row with increasing values
            # Bottom row index for column c is R
            # Top row index for column c is c
            for i in range(num_elements):
                row = R - i  # R, R-1, ..., c
                grid[row][c] = start_val + i
        else:
            # Fill from top row to bottom row with increasing values
            # Top row index for column c is c
            # Bottom row index for column c is R
            for i in range(num_elements):
                row = c + i  # c, c+1, ..., R
                grid[row][c] = start_val + i
        
        cnt += num_elements
    
    # Now print the grid
    # Row r has elements from column 1 to column r
    output_lines = []
    for r in range(1, R + 1):
        row_vals = [str(grid[r][c]) for c in range(1, r + 1)]
        output_lines.append(' '.join(row_vals))
    
    print('\n'.join(output_lines))

if __name__ == '__main__':
    solve()
