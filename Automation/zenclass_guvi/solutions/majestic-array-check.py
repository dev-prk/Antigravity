import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n])) if n > 0 else []
    if len(arr) < 3:
        print(0)
        return
    print(1 if sum(arr[:3]) == sum(arr[-3:]) else 0)

if __name__ == "__main__":
    main()
