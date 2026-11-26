import sys
import math

def is_stiff(n):
    if n <= 2:
        return n == 2
    return True

def main():
    n = int(sys.stdin.readline().strip())
    if is_stiff(n):
        print("Stiff")
    else:
        print("not stiff")

if __name__ == "__main__":
    main()
