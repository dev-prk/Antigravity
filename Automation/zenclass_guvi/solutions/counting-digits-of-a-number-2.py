import sys

def main():
    data = sys.stdin.read().split()
    for token in data:
        n = int(token)
        if n == 0:
            print(1)
        else:
            print(len(str(abs(n))))

if __name__ == "__main__":
    main()
