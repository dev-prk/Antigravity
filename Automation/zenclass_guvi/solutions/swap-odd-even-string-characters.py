import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = []
    for i in range(0, len(s) - 1, 2):
        result.append(s[i+1])
        result.append(s[i])
    if len(s) % 2 == 1:
        result.append(s[-1])
    print(''.join(result))

if __name__ == "__main__":
    main()
