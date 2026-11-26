import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 3:
        return
    p, r, t = map(float, data[:3])
    si = p * r * t / 100
    print(f"{si:.2f}")

if __name__ == "__main__":
    main()
