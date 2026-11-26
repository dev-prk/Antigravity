import sys

def solve():
    lines = [line.rstrip('\n') for line in sys.stdin.readlines()]
    if not lines:
        return
    # The last line is the query name, the rest are student names
    *names, query = lines
    unique_names = set(names)
    out = []
    out.append(f"Unique Names Count: {len(unique_names)}")
    out.append("Name Found" if query in unique_names else "Name Not Found")
    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    solve()
