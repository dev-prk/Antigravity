import sys

def main():
    R = int(sys.stdin.readline().strip())
    
    for i in range(1, R + 1):
        if i == 1:
            # First row: single '1'
            print(" " * (R - 1) + "1")
        elif i == R:
            # Last row: full pyramid
            print(" ".join(str(j) for j in range(1, R + 1)))
        else:
            # Hollow part
            # Leading spaces: R - i
            # Then: 1, spaces, then i
            spaces_between = " " * (2 * i - 3)
            print(" " * (R - i) + "1" + spaces_between + str(i))

if __name__ == "__main__":
    main()
