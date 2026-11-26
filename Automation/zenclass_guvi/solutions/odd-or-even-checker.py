import sys
import math

def main():
    data = sys.stdin.read().strip()
    if not data:
        print("Zero")
        return
    try:
        num = float(data)
    except ValueError:
        print("Zero")
        return
    # round to nearest integer (half away from zero)
    if num >= 0:
        rounded = int(math.floor(num + 0.5))
    else:
        rounded = int(math.ceil(num - 0.5))
    if rounded == 0:
        print("Zero")
    elif rounded % 2 == 0:
        print("Even")
    else:
        print("Odd")

if __name__ == "__main__":
    main()
