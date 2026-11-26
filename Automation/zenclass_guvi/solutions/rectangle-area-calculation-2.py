import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    # Take the first two numbers (width and height). If only one is given, default the other to 1.0.
    a = float(data[0])
    b = float(data[1]) if len(data) > 1 else 1.0
    area = a * b
    # Round to 2 decimal places and always display with exactly two digits after the decimal point.
    print(f"{round(area, 2):.2f}")

if __name__ == "__main__":
    solve()
