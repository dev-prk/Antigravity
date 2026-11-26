import sys

def main():
    s = sys.stdin.read().strip()
    if not s:
        print("no")
        return
    
    stack = []
    matching = {')': '(', '}': '{', ']': '['}
    opening = {'(', '{', '['}
    closing = {')', '}', ']'}
    
    for ch in s:
        if ch in opening:
            stack.append(ch)
        elif ch in closing:
            if not stack or stack[-1] != matching[ch]:
                print("no")
                return
            stack.pop()
    
    if len(stack) == 0:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
