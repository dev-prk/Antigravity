import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    stack = []
    for char in s:
        stack.append(char)
    reversed_str = ""
    while stack:
        reversed_str += stack.pop()
    print(reversed_str)

if __name__ == "__main__":
    main()
