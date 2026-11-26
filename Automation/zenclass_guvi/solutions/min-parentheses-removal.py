def main():
    import sys
    S = sys.stdin.read().strip()
    
    stack = []
    remove_indices = set()
    
    for i, char in enumerate(S):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                stack.pop()
            else:
                remove_indices.add(i)
    
    while stack:
        remove_indices.add(stack.pop())
    
    result = []
    for i, char in enumerate(S):
        if i not in remove_indices:
            result.append(char)
    
    print(''.join(result))

if __name__ == "__main__":
    main()
