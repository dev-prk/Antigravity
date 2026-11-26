import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    A = int(data[0])
    B = int(data[1])
    C = int(data[2])
    if C == 1:
        print(0)
    else:
        print(pow(A % C, B, C))

if __name__ == "__main__":
    main()
