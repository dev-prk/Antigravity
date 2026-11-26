import sys

def main():
    # Read three lines from input
    line1 = sys.stdin.readline().strip()
    line2 = sys.stdin.readline().strip()
    line3 = sys.stdin.readline().strip()
    
    # Convert to integers
    a = int(line1)
    b = int(line2)
    c = int(line3)
    
    # Print in single line separated by space
    print(f"{a} {b} {c}")

if __name__ == "__main__":
    main()
