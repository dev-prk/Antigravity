import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    count = 0
    for s in data[1:1 + n]:
        if int(s) % 2 != 0:
            count += 1
    print(count)

if __name__ == "__main__":
    main()
