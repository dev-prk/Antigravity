import sys

def main():
    data = list(map(int, sys.stdin.read().split()))
    r1, c1, r2, c2 = data[0], data[1], data[2], data[3]
    if abs(r1 - r2) == abs(c1 - c2):
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
