import sys

def main():
    # Read all lines and strip whitespace
    lines = [line.strip() for line in sys.stdin.readlines()]
    
    # Handle empty input
    if not lines:
        print("no")
        return
    
    # Parse first line - matrix dimensions
    first_line = lines[0].split()
    rows = int(first_line[0])
    cols = int(first_line[1])
    
    # Parse second line - matrix elements
    elements = list(map(int, lines[1].split()))
    
    # Parse third line - target to search
    target = int(lines[2])
    
    # Search in the matrix (O(n*m))
    found = False
    count = 0
    for elem in elements:
        if count < rows * cols:
            if elem == target:
                found = True
                break
            count += 1
    
    # Output result
    if found:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
