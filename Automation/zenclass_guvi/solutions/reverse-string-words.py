import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    words = s.split()
    reversed_words = [word[::-1] for word in words]
    print(' '.join(reversed_words))

if __name__ == "__main__":
    main()
