import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    N = int(data[0])
    K = int(data[1])
    
    # Perform bitwise right shift K times
    result = N >> K
    
    # Round to 2 decimal places and print
    print(round(result, 2))

if __name__ == "__main__":
    main()
