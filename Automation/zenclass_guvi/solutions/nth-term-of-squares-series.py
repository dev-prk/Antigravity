import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n < 0:
        print("Error")
    elif n == 0:
        print(0)
    else:
        print(n * n)

if __name__ == "__main__":
    main()
