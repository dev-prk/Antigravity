s = input().strip()
stack = []
for c in s:
    if c == '(':
        stack.append(c)
    else:
        if not stack:
            print("Not Balanced")
            exit()
        stack.pop()
print("Balanced" if not stack else "Not Balanced")
