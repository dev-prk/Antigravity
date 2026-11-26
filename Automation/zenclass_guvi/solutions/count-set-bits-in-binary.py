import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    # Assuming non-negative integer as per typical problem constraints
    # If negative numbers need two's complement handling, problem would specify.
    # Using Python's built-in bin and count for clarity and efficiency.
    print(bin(n).count('1'))

if __name__ == "__main__":
    main()
