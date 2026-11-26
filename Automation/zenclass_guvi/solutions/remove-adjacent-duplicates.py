import sys

def remove_adjacent_duplicates(s):
    result = []
    for char in s:
        if result and result[-1] == char:
            result.pop()
        else:
            result.append(char)
    return ''.join(result)

def main():
    s = sys.stdin.readline().rstrip('\n')
    result = remove_adjacent_duplicates(s)
    print(result)

if __name__ == "__main__":
    main()
