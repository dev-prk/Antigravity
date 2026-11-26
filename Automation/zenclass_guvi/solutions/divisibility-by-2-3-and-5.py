import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n % 2 == 0 and n % 3 == 0 and n % 5 == 0:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
