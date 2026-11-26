import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    s = data[0]
    try:
        a = int(s)
    except ValueError:
        a = float(s)
    meters = a * 1000
    centimeters = a * 100000
    # Convert to int if whole number
    if isinstance(meters, float) and meters.is_integer():
        meters = int(meters)
    if isinstance(centimeters, float) and centimeters.is_integer():
        centimeters = int(centimeters)
    sys.stdout.write(f"{meters}\n{centimeters}")

if __name__ == "__main__":
    solve()
