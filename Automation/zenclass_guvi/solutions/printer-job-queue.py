import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("Queue Empty")
        return
    
    n = int(data[0])
    
    if n == 0:
        print("Queue Empty")
        return
    
    jobs = list(map(int, data[1:1+n]))
    
    if not jobs:
        print("Queue Empty")
        return
    
    queue = deque(jobs)
    queue.popleft()
    
    if queue:
        print(f"Next Job: {queue[0]}")
    else:
        print("Queue Empty")

if __name__ == "__main__":
    main()
