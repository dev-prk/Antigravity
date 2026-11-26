import sys

def main():
    data = sys.stdin.read().strip().split()
    a, b, c, d = map(int, data)
    area1 = a * b
    perim1 = 2 * (a + b)
    area2 = c * d
    perim2 = 2 * (c + d)
    print(area1, perim1)
    print(area2, perim2)

if __name__ == "__main__":
    main()
