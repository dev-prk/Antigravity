import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    row_count = int(data[0])
    col_count = int(data[1])
    
    if row_count == 0 or col_count == 0:
        print(0)
        return
    
    elements = list(map(int, data[2:2 + row_count * col_count]))
    
    matrix = []
    idx = 0
    for i in range(row_count):
        row = []
        for j in range(col_count):
            row.append(elements[idx])
            idx += 1
        matrix.append(row)
    
    total = 0
    
    for i in range(min(row_count, col_count)):
        total += matrix[i][i]
    
    for i in range(min(row_count, col_count)):
        j = col_count - 1 - i
        if i != j:
            total += matrix[i][j]
    
    print(total)

if __name__ == "__main__":
    main()
