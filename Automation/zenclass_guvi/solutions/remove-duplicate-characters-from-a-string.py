import sys

def remove_duplicates(s):
    seen = set()
    result = []
    for char in s:
        if char not in seen:
            seen.add(char)
            result.append(char)
    return ''.join(result)

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = remove_duplicates(s)
    print(result)

if __name__ == "__main__":
    main()
