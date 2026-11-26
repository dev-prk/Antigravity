import sys
import math

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        r = float(data[0])
    except ValueError:
        return
    if r == 0:
        print("None")
    else:
        area = math.pi * r * r
        print(f"{area:.2f}")

if __name__ == "__main__":
    main()
