import sys

def main():
    n = int(sys.stdin.readline().strip())
    
    if n == 1:
        print("*")
        return
    
    # First line: n stars with leading spaces (n-1 spaces)
    print(" " * (n - 1) + "*" * n)
    
    # Middle lines: hollow part
    for i in range(n - 2):
        spaces_before = n - 2 - i
        spaces_middle = n - 2
        print(" " * spaces_before + "*" + " " * spaces_middle + "*")
    
    # Last line: n stars, no leading spaces
    print("*" * n)

if __name__ == "__main__":
    main()
