import sys
import math

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    diameter = int(line)
    radius = diameter / 2.0
    area = math.pi * radius * radius
    print("{:.2f}".format(area))

if __name__ == "__main__":
    main()
