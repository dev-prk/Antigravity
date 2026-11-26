import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        a = int(data[0])
    except ValueError:
        # fallback to float if not integer
        a = float(data[0])
    area = 6 * a * a
    volume = a * a * a
    # If results are integers (no decimal part), print as int
    if isinstance(area, float) and area.is_integer():
        area = int(area)
    if isinstance(volume, float) and volume.is_integer():
        volume = int(volume)
    sys.stdout.write(f"{area}\n{volume}")

if __name__ == "__main__":
    solve()
