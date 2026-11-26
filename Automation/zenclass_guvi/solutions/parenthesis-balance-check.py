s = input().strip()
stack = []
mapping = {')': '(', '}': '{', ']': '['}
for char in s:
    if char in '({[':
        stack.append(char)
    elif char in ')}]':
        if not stack or stack[-1] != mapping[char]:
            print(0)
            exit()
        stack.pop()
print(1 if not stack else 0)
