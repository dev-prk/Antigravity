import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    elements = data[1:n+1]
    print(len(elements))

if __name__ == "__main__":
    main()
