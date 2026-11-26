import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    parts = data[0].split(maxsplit=2)
    if len(parts) < 3:
        return
    N = int(parts[0])
    M = int(parts[1])
    name = parts[2]

    children = {}
    for i in range(1, 1 + M):
        line = data[i].split()
        if len(line) < 2:
            continue
        p, c = line[0], line[1]
        if p not in children:
            children[p] = []
        children[p].append(c)

    if name not in children:
        print(0)
        return

    total = 0
    for child in children[name]:
        total += len(children.get(child, []))
    print(total)

if __name__ == "__main__":
    main()
