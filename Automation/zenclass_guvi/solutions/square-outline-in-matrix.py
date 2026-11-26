import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("NO")
        return
    
    M = int(data[0])
    N = int(data[1])
    
    if M < 2 or N < 2:
        print("NO")
        return
    
    matrix = []
    index = 2
    for i in range(M):
        row = list(map(int, data[index:index+N]))
        matrix.append(row)
        index += N
    
    max_side = min(M, N)
    
    for side in range(2, max_side + 1):
        for r in range(M - side + 1):
            for c in range(N - side + 1):
                valid = True
                
                for j in range(c, c + side):
                    if matrix[r][j] != 4:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                for j in range(c, c + side):
                    if matrix[r + side - 1][j] != 4:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                for i in range(r + 1, r + side - 1):
                    if matrix[i][c] != 4:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                for i in range(r + 1, r + side - 1):
                    if matrix[i][c + side - 1] != 4:
                        valid = False
                        break
                
                if valid:
                    print("YES")
                    return
    
    print("NO")

if __name__ == "__main__":
    main()
