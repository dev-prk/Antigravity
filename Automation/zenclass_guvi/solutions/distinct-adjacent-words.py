import sys

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print(-1)
        return
    
    words = s.split()
    
    # Use a stack approach to remove adjacent identical words
    stack = []
    for word in words:
        if stack and stack[-1] == word:
            stack.pop()
        else:
            stack.append(word)
    
    if not stack:
        print(-1)
    else:
        print(' '.join(stack))

if __name__ == "__main__":
    main()
