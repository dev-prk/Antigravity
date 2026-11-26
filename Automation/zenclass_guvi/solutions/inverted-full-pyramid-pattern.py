import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    R = int(data[0])
    
    for i in range(R):
        # i leading spaces
        # (R - i) stars, each separated by space
        leading_spaces = ' ' * i
        num_stars = R - i
        stars = ' '.join(['*'] * num_stars)
        print(leading_spaces + stars)

if __name__ == "__main__":
    main()
