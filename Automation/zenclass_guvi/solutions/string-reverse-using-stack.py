import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    words = s.split()
    stack = []
    for word in words:
        stack.append(word)
    reversed_words = []
    while stack:
        reversed_words.append(stack.pop())
    print(' '.join(reversed_words))

if __name__ == "__main__":
    main()
