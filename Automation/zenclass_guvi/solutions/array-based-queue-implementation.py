import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        if len(data) < 2:
            return
        o = int(data[1])
        if o == 1 and len(data) >= 3:
            x = int(data[2])
            print(x)
        elif o == 2:
            print(-1)
        return
    
    queue = list(map(int, data[1:1+n]))
    
    idx = 1 + n
    if idx >= len(data):
        print(' '.join(map(str, queue)))
        return
    
    o = int(data[idx])
    
    if o == 1:
        if idx + 1 < len(data):
            x = int(data[idx + 1])
            queue.append(x)
        print(' '.join(map(str, queue)))
    elif o == 2:
        if queue:
            queue.pop(0)
        print(' '.join(map(str, queue)) if queue else '-1')

if __name__ == "__main__":
    main()
