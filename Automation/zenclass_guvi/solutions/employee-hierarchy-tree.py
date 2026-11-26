import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0 or len(data) < 2:
        print("Root Employee: -1")
        return
    root = int(data[1])
    print(f"Root Employee: {root}")

if __name__ == "__main__":
    main()
