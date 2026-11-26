import sys

def main():
    R = int(sys.stdin.readline().strip())
    for i in range(1, R + 1):
        print(str(i) * i)

if __name__ == "__main__":
    main()
