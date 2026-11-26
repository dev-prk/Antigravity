import sys

def main():
    s = sys.stdin.read().rstrip('\n')
    words = s.split()
    i = 0
    n = len(words)
    while i < n:
        if words[i] == 'and':
            if i > 0 and i + 1 < n:
                words[i-1], words[i+1] = words[i+1], words[i-1]
            i += 1
        else:
            i += 1
    sys.stdout.write(' '.join(words))

if __name__ == "__main__":
    main()
