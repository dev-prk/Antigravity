import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n & 1:
        print("Odd")
    else:
        print("Even")

if __name__ == "__main__":
    main()
