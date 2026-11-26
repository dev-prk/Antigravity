import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    m = int(data[0])
    n = int(data[1])
    
    if m == 0 or n == 0:
        return
    
    matrix = []
    index = 2
    for i in range(m):
        row = list(map(int, data[index:index+n]))
        matrix.append(row)
        index += n
    
    result = [[0] * n for _ in range(m)]
    
    for i in range(m):
        for j in range(n):
            total = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n:
                        total += matrix[ni][nj]
            result[i][j] = total
    
    for row in result:
        print(' '.join(map(str, row)))

if __name__ == "__main__":
    main()
