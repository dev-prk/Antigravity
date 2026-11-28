import sys

def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.strip())
    
    matrix1 = []
    matrix2 = []
    
    for i in range(2):
        row = list(map(int, lines[i].split()))
        matrix1.append(row)
    
    for i in range(2, 4):
        row = list(map(int, lines[i].split()))
        matrix2.append(row)
    
    result = []
    for i in range(2):
        row = []
        for j in range(2):
            row.append(matrix1[i][j] + matrix2[i][j])
        result.append(row)
    
    for row in result:
        print(' '.join(map(str, row)) + ' ')

if __name__ == "__main__":
    main()
