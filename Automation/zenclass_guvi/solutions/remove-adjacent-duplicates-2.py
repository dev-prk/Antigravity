import sys

def remove_adjacent_duplicates(s):
    stack = []
    for char in s:
        if stack and stack[-1] == char:
            stack.pop()
        else:
            stack.append(char)
    return ''.join(stack) if stack else -1

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print(-1)
        return
    result = remove_adjacent_duplicates(s)
    if result == -1:
        print(-1)
    else:
        print(result)

if __name__ == "__main__":
    main()
