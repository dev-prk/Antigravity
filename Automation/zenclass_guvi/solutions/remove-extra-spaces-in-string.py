import sys

def main():
    line = sys.stdin.readline()
    words = line.split()
    result = ' '.join(words)
    print(result)

if __name__ == "__main__":
    main()
