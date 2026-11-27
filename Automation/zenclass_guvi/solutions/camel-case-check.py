import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    if not s:
        print('no')
        return
    words = []
    current = s[0]
    for i in range(1, len(s)):
        if s[i].isupper():
            words.append(current)
            current = s[i]
        else:
            current += s[i]
    words.append(current)
    if len(words) >= 2 and all(word[0].isupper() and word[1:].islower() for word in words):
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
