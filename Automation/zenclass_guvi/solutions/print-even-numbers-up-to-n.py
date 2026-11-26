import sys

def main():
    data = sys.stdin.readline()
    if not data:
        return
    N = int(data.strip())
    for i in range(2, N + 1, 2):
        print(i)

if __name__ == "__main__":
    main()
