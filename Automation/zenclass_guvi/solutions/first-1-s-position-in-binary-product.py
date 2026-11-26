import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    a, b = map(int, data[:2])
    prod = a * b
    if prod == 0:
        print(0)
        return
    prod = abs(prod)
    binary = bin(prod)[2:]          # binary string without '0b'
    second_one_idx = binary.find('1', 1)  # search after the first character
    if second_one_idx == -1:
        print(0)
    else:
        print(second_one_idx + 1)   # convert to 1‑based position

if __name__ == "__main__":
    solve()
