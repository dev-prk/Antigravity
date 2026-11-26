import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    rows = int(data[0])
    cols = int(data[1])
    
    matrix = []
    index = 2
    for i in range(rows):
        row = list(map(int, data[index:index + cols]))
        matrix.append(row)
        index += cols
    
    transpose = [[matrix[i][j] for i in range(rows)] for j in range(cols)]
    
    for row in transpose:
        print(' '.join(map(str, row)))

if __name__ == "__main__":
    main()
