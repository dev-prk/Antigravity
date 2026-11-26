import sys

def main():
    data = sys.stdin.read()
    if not data:
        return
    words = data.split()
    for i in range(0, len(words), 2):
        words[i] = words[i][::-1]
    sys.stdout.write(' '.join(words))

if __name__ == "__main__":
    main()
