import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split()
    if len(parts) < 2:
        return
    a = int(parts[0])
    b = int(parts[1])
    total = a + b
    binary = bin(total)[2:]
    print(binary)

if __name__ == "__main__":
    main()
