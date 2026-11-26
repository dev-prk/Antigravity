import sys

def main():
    s = sys.stdin.readline().strip()
    if not s:
        return
    words = s.split()
    words.sort()
    print(' '.join(words))

if __name__ == "__main__":
    main()
