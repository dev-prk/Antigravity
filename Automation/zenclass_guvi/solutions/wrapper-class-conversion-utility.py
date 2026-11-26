import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    string_value = data[0]
    try:
        int_value = int(string_value)
    except ValueError:
        # If parsing fails, treat as zero
        int_value = 0
    double_value = float(int_value)
    after_addition = int_value + 100
    print(f"String Value: {string_value}")
    print(f"Integer Value: {int_value}")
    print(f"Double Value: {double_value}")
    print(f"After Addition: {after_addition}")

if __name__ == "__main__":
    solve()
