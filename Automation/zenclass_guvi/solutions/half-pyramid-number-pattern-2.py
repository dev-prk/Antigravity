import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    R = int(data[0])
    for i in range(1, R + 1):
        length = R - i + 1
        if i % 2 == 1:
            print(''.join(str(j) for j in range(1, length + 1)))
        else:
            print(''.join(str(j) for j in range(length, 0, -1)))

if __name__ == "__main__":
    main()
