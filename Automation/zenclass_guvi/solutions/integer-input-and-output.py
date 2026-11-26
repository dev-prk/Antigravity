import sys

def main():
    data = sys.stdin.read().split()
    if data:
        print(int(data[0]))

if __name__ == "__main__":
    main()
