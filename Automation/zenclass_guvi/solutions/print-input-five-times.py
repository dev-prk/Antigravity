import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    n = int(line.strip())
    for _ in range(5):
        print(n)

if __name__ == "__main__":
    main()
