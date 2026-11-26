import sys

def main():
    s = sys.stdin.readline().strip()
    
    if not s:
        print("Not Balanced")
        return
    
    stack = []
    opening = "({["
    closing = ")}]"
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in opening:
            stack.append(char)
        elif char in closing:
            if not stack:
                print("Not Balanced")
                return
            if stack[-1] != mapping[char]:
                print("Not Balanced")
                return
            stack.pop()
    
    if stack:
        print("Not Balanced")
    else:
        print("Balanced")

if __name__ == "__main__":
    main()
