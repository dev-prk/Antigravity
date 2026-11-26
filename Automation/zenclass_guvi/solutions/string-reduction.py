import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print(0)
        return
    
    n = int(data[0].strip())
    if len(data) < 2:
        words = []
    else:
        words = data[1].strip().split()
    
    stack = []
    for word in words:
        if stack and stack[-1] == word:
            stack.pop()
        else:
            stack.append(word)
    
    print(len(stack))

if __name__ == "__main__":
    main()
