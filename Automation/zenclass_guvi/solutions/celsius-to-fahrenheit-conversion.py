import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    c = float(data)
    f = (c * 9.0 / 5.0) + 32.0
    print(f"{f:.2f}")

if __name__ == "__main__":
    main()
