import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    words = line.split()
    n = len(words)
    if n <= 2:
        print(line)
    else:
        reversed_middle = [word[::-1] for word in words[1:-1]]
        result = [words[0]] + reversed_middle + [words[-1]]
        print(' '.join(result))

if __name__ == "__main__":
    main()
