import sys

def main():
    R = int(sys.stdin.readline().strip())
    for i in range(R, 0, -1):
        print(str(i) * i)

if __name__ == "__main__":
    main()
