import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    words = s.split()
    result = []
    for i, word in enumerate(words):
        if i % 2 == 0:
            result.append(word.upper())
        else:
            result.append(word.lower())
    print(' '.join(result))

if __name__ == "__main__":
    main()
