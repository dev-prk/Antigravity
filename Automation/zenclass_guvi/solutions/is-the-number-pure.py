import sys

def solve() -> None:
    data = sys.stdin.read().strip()
    # Sum the digits, ignoring any non-digit characters (e.g. a leading minus sign)
    digit_sum = sum(int(c) for c in data if c.isdigit())
    print("yes" if digit_sum % 3 == 0 else "not")

if __name__ == "__main__":
    solve()
