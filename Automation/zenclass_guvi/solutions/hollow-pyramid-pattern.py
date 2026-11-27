import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(-1)
        return
    
    try:
        R = int(data[0])
    except (ValueError, IndexError):
        print(-1)
        return
    
    if R < 1 or R > 100:
        print(-1)
        return
    
    # Generate hollow full pyramid
    # For each row i (1-indexed), from 1 to R
    for i in range(1, R + 1):
        if i == 1:
            # First row: single star centered
            spaces = " " * (R - 1)
            print(spaces + "*")
        elif i == R:
            # Last row: full base
            stars = "* " * R
            print(stars.rstrip())
        else:
            # Middle rows: hollow
            # Leading spaces
            leading_spaces = " " * (R - i)
            # First star
            # Middle spaces (between the two stars)
            middle_spaces = " " * (2 * i - 3)
            # Second star
            print(leading_spaces + "*" + middle_spaces + "*")

if __name__ == "__main__":
    main()
