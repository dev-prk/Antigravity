import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    R = int(data[0])
    
    for i in range(R):
        # Calculate leading spaces: (R-1-i) spaces
        leading_spaces = ' ' * (R - 1 - i)
        
        # Build the number sequence for row i
        # Numbers go from i down to 0, then up to i
        # For row i=2: 2 1 0 1 2
        left_part = ''.join(str(j) for j in range(i, 0, -1))
        middle = '0'
        right_part = ''.join(str(j) for j in range(1, i + 1))
        
        row = leading_spaces + left_part + middle + right_part
        print(row)

if __name__ == "__main__":
    main()
