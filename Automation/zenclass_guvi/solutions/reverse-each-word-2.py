import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    line = line.rstrip('\n')
    result = []
    word = []
    for ch in line:
        if ch == ' ':
            if word:
                result.append(''.join(reversed(word)))
                word = []
            result.append(' ')
        else:
            word.append(ch)
    if word:
        result.append(''.join(reversed(word)))
    sys.stdout.write(''.join(result))

if __name__ == "__main__":
    main()
