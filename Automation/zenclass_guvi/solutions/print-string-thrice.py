import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = (s + ' ') * 3
    result = result.rstrip()
    print(result)

if __name__ == "__main__":
    main()
