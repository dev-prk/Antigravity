import sys

def solve() -> None:
    data = sys.stdin.read().splitlines()
    if not data:
        print("NO")
        return
    n = int(data[0].strip())
    first_to_second = {}
    for i in range(1, n + 1):
        parts = data[i].split()
        if len(parts) < 2:
            continue
        a, b = parts[0], parts[1]
        first_to_second[a] = b
    for a, b in first_to_second.items():
        if b in first_to_second and first_to_second[b] == a:
            print("YES")
            return
    print("NO")

if __name__ == "__main__":
    solve()
