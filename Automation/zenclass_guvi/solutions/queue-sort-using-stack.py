import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("No")
        return
    
    n = int(data[0])
    if n == 0:
        print("Yes")
        return
    
    arr = list(map(int, data[1:n+1]))
    
    expected = 1
    stack = []
    queue = deque(arr)
    
    while queue or stack:
        if stack and stack[-1] == expected:
            stack.pop()
            expected += 1
        elif queue and queue[0] == expected:
            queue.popleft()
            expected += 1
        elif queue:
            stack.append(queue.popleft())
        else:
            print("No")
            return
    
    print("Yes")

if __name__ == "__main__":
    main()
