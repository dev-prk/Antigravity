import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = sum(ord(c) for c in s)
    print(result)

if __name__ == "__main__":
    main()
