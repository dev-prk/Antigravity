import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(1)
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    total = sum(arr)
    if total % 2 == 0 and total % 3 == 0 and total % 5 == 0:
        print(1)
    else:
        print(0)

if __name__ == "__main__":
    main()
