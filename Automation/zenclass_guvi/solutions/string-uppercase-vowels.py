import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = []
    for char in s:
        if char in 'aeiou':
            result.append(char.upper())
        else:
            result.append(char)
    print(''.join(result))

if __name__ == "__main__":
    main()
