import sys

def reverse_middle(s):
    if len(s) <= 2:
        return s
    return s[0] + s[1:-1][::-1] + s[-1]

def main():
    line = sys.stdin.readline()
    words = line.strip().split()
    result = [reverse_middle(word) for word in words]
    print(' '.join(result))

if __name__ == "__main__":
    main()
