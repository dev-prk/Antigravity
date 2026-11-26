import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = []
    word = []
    
    for char in s:
        if char == ' ':
            if word:
                result.append(''.join(reversed(word)))
                word = []
            result.append(' ')
        else:
            word.append(char)
    
    if word:
        result.append(''.join(reversed(word)))
    
    sys.stdout.write(''.join(result))

if __name__ == "__main__":
    main()
