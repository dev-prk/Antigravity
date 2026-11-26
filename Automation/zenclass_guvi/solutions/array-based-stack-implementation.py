import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    stack = []
    idx = 1
    
    if n > 0:
        for i in range(n):
            stack.append(int(data[idx]))
            idx += 1
    
    if idx < len(data):
        op = int(data[idx])
        idx += 1
        if op == 1:
            x = int(data[idx])
            stack.append(x)
        elif op == 2:
            if stack:
                stack.pop()
    
    print(' '.join(map(str, stack)))

if __name__ == "__main__":
    main()
