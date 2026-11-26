import sys

def main():
    # The fixed 5x5 matrix with the string "WELCOMETOGUVICORPORATIONS"
    matrix = [
        ['W', 'E', 'L', 'C', 'O'],
        ['M', 'E', 'T', 'O', 'G'],
        ['U', 'G', 'U', 'V', 'I'],
        ['C', 'O', 'R', 'P', 'O'],
        ['R', 'A', 'T', 'I', 'O']
    ]
    
    # Read the substring to search for
    substring = sys.stdin.readline().strip()
    
    if not substring:
        print(0)
        return
    
    n = len(substring)
    
    # Search in horizontal direction (left to right)
    for i in range(5):
        for j in range(5 - n + 1):
            match = True
            for k in range(n):
                if matrix[i][j + k] != substring[k]:
                    match = False
                    break
            if match:
                print(f"{i} {j}")
                print(f"{i} {j + n - 1}")
                return
    
    # Search in vertical direction (top to bottom)
    for i in range(5 - n + 1):
        for j in range(5):
            match = True
            for k in range(n):
                if matrix[i + k][j] != substring[k]:
                    match = False
                    break
            if match:
                print(f"{i} {j}")
                print(f"{i + n - 1} {j}")
                return
    
    print(0)

if __name__ == "__main__":
    main()
