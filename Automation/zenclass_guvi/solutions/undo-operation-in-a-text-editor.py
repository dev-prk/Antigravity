import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("Nothing To Undo")
        return
    
    n = int(data[0])
    
    if n == 0:
        print("Nothing To Undo")
        return
    
    if len(data) < 1 + n:
        print("Nothing To Undo")
        return
    
    stack = list(map(int, data[1:1+n]))
    
    if len(stack) == 0:
        print("Nothing To Undo")
        return
    
    stack.pop()
    
    if len(stack) == 0:
        print("Nothing To Undo")
    else:
        print(f"Last Action: {stack[-1]}")

if __name__ == "__main__":
    main()
