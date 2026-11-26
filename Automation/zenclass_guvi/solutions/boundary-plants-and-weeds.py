import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print("0 0")
        return
    
    n = int(data[0].strip())
    
    if n == 0:
        print("0 0")
        return
    
    matrix = []
    for i in range(1, n + 1):
        if i < len(data):
            row = data[i].strip()
            matrix.append(row)
        else:
            matrix.append("")
    
    plants = 0
    weeds = 0
    
    for i in range(n):
        for j in range(n):
            if i == 0 or i == n - 1 or j == 0 or j == n - 1:
                if matrix[i][j] == '.':
                    plants += 1
                elif matrix[i][j] == '#':
                    weeds += 1
    
    print(f"{plants} {weeds}")

if __name__ == "__main__":
    main()
