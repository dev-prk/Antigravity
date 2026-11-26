import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    count = 0
    for i in range(2, 2 + n):
        if int(data[i]) == k:
            count += 1
    if count:
        print("yes", count)
    else:
        print("no")

if __name__ == "__main__":
    main()
