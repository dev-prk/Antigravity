import sys

def main():
    data = sys.stdin.read()
    words = data.split()
    words.sort(key=len)
    sys.stdout.write(" ".join(words))

if __name__ == "__main__":
    main()
