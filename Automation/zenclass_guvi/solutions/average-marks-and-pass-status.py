import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    marks = list(map(int, data))
    a, b, c = marks
    avg = (a + b + c) / 3
    print(f"{avg:.2f}")
    print(str(avg >= 40 and a >= 35 and b >= 35 and c >= 35))

if __name__ == "__main__":
    main()
