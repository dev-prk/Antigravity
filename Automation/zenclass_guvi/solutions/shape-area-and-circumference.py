import sys
import math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    choice = int(data[0])
    
    if choice == 1:  # Circle
        r = float(data[1])
        area = math.pi * r * r
        circumference = 2 * math.pi * r
        print(f"{area:.2f}" if area != int(area) else f"{int(area)}")
        print(f"{circumference:.2f}" if circumference != int(circumference) else f"{int(circumference)}")
    elif choice == 2:  # Square
        a = float(data[1])
        area = a * a
        circumference = 4 * a
        print(f"{area:.2f}" if area != int(area) else f"{int(area)}")
        print(f"{circumference:.2f}" if circumference != int(circumference) else f"{int(circumference)}")
    elif choice == 3:  # Rectangle
        l = float(data[1])
        b = float(data[2])
        area = l * b
        circumference = 2 * (l + b)
        print(f"{area:.2f}" if area != int(area) else f"{int(area)}")
        print(f"{circumference:.2f}" if circumference != int(circumference) else f"{int(circumference)}")

if __name__ == "__main__":
    main()
