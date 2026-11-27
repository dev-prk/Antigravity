n = int(input().strip())
current = 1
result = []

for i in range(n):
    row = []
    for j in range(n):
        if i % 2 == 0:
            # Right row: left to right, but we want descending in output
            # Actually the pattern shows descending on right rows
            pass
        row.append(current)
        current += 1
    
    if i % 2 == 0:
        # Right movement (row 0, 2, 4...): reverse the row
        row = row[::-1]
    
    result.append(' '.join(map(str, row)))

print('\n'.join(result))
