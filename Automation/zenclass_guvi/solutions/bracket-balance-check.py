import sys

def is_balanced(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack[-1] != mapping[char]:
                return 'no'
            stack.pop()
    
    return 'yes' if not stack else 'no'

def main():
    s = sys.stdin.readline().strip()
    print(is_balanced(s))

if __name__ == "__main__":
    main()
