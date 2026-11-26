import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    words = line.strip().split()
    words.reverse()
    print(' '.join(words))

if __name__ == "__main__":
    main()
