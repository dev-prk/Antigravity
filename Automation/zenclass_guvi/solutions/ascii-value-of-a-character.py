import sys

def main():
    data = sys.stdin.read().strip()
    if data:
        print(ord(data[0]))

if __name__ == "__main__":
    main()
