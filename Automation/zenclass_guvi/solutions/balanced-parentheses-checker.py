import sys

def check_balanced(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack[-1] != mapping[char]:
                return "Not Balanced"
            stack.pop()
    
    return "Balanced" if not stack else "Not Balanced"

def main():
    s = sys.stdin.readline().strip()
    print(check_balanced(s))

if __name__ == "__main__":
    main()
