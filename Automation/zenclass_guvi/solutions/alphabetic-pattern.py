import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    for i in range(1, n + 1):
        print(chr(ord('a') + i - 1) * i)

if __name__ == "__main__":
    main()
