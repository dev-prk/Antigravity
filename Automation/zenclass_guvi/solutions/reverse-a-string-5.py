import sys

def main():
    data = sys.stdin.read()
    words = data.split()
    print(' '.join(words[::-1]))

if __name__ == '__main__':
    main()
