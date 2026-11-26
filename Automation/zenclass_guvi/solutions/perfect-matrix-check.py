import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("yes")
        return
    
    n = int(data[0])
    
    if n == 0:
        print("yes")
        return
    
    if len(data) < 1 + n * n:
        print("no")
        return
    
    matrix = []
    idx = 1
    for i in range(n):
        row = list(map(int, data[idx:idx + n]))
        idx += n
        matrix.append(row)
    
    for i in range(n):
        if matrix[i][i] % 2 != 0:
            print("no")
            return
        if matrix[i][n - 1 - i] % 2 != 0:
            print("no")
            return
    
    print("yes")

if __name__ == "__main__":
    main()
