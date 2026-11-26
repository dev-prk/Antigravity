import sys

def main():
    n = int(sys.stdin.readline().strip())
    
    for i in range(n):
        row = []
        for j in range(n):
            # Check if on border
            if i == 0 or i == n - 1 or j == 0 or j == n - 1:
                # Check if on main or anti diagonal
                if i == j or i + j == n - 1:
                    row.append('M')
                else:
                    row.append('F')
            else:
                # Check if on main or anti diagonal
                if i == j or i + j == n - 1:
                    row.append('M')
                else:
                    row.append('C')
        print(' '.join(row))

if __name__ == "__main__":
    main()
