import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split()
    if len(parts) < 2:
        return
    a, b = int(parts[0]), int(parts[1])
    print(min(a, b))

if __name__ == "__main__":
    main()
