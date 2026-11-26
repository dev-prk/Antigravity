import sys

def main():
    q = int(sys.stdin.readline().strip())
    stack = []
    
    for _ in range(q):
        line = sys.stdin.readline().strip()
        parts = line.split()
        
        if parts[0] == "PUSH":
            # parts[1] is the number to push as string
            x = int(parts[1])
            stack.append(x)
        elif parts[0] == "POP":
            if stack:
                print(stack.pop())
            else:
                print("Stack is empty")
        elif parts[0] == "PEEK":
            if stack:
                print(stack[-1])
            else:
                print("Stack is empty")

if __name__ == "__main__":
    main()
