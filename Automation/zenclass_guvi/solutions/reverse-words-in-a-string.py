import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    words = line.strip().split()
    reversed_words = [word[::-1] for word in words]
    print(' '.join(reversed_words))

if __name__ == "__main__":
    main()
