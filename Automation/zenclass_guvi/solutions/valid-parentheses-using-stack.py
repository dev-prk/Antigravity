def main():
    import sys
    s = sys.stdin.readline().strip()
    
    if not s:
        print("Not Balanced")
        return
    
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack[-1] != mapping[char]:
                print("Not Balanced")
                return
            stack.pop()
    
    if len(stack) == 0:
        print("Balanced")
    else:
        print("Not Balanced")

if __name__ == "__main__":
    main()
