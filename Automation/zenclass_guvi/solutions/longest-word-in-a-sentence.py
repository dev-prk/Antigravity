import sys

def main():
    line = sys.stdin.readline()
    words = line.strip().split()
    if not words:
        print(-1)
        return
    max_word = words[0]
    max_len = len(max_word)
    for word in words[1:]:
        if len(word) > max_len:
            max_len = len(word)
            max_word = word
    print(max_word)

if __name__ == "__main__":
    main()
