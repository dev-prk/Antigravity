import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    if n <= 0:
        return
    for i in range(n, 0, -1):
        print(" ".join(["1"] * i))

if __name__ == "__main__":
    main()
