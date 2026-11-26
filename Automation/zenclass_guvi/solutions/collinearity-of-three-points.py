import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 6:
        return
    x1, y1, x2, y2, x3, y3 = map(int, data[:6])
    # Three points are collinear if the area of the triangle they form is zero.
    # Using cross product: (x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1) == 0
    if (x2 - x1) * (y3 - y1) == (y2 - y1) * (x3 - x1):
        print('yes')
    else:
        print('no')

if __name__ == '__main__':
    main()
