import sys

def hollow_rectangle_star_pattern(r: int, c: int) -> None:
    for i in range(r):
        if i == 0 or i == r - 1:
            print(' '.join(['*'] * c))
        else:
            print('*' + ' ' * (2 * c - 3) + '*')

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    r = int(data[0])
    c = int(data[1])
    hollow_rectangle_star_pattern(r, c)

if __name__ == "__main__":
    main()
