import sys

def main():
    # Read the first line for n
    n_line = sys.stdin.readline()
    n = int(n_line.strip())
    
    # Handle edge case of n = 0
    if n == 0:
        print(-1)
        return
    
    # Read the second line for elements
    elements_line = sys.stdin.readline()
    elements = list(map(int, elements_line.split()))
    
    # Find and print minimum element
    minimum = min(elements)
    print(minimum)

if __name__ == "__main__":
    main()
