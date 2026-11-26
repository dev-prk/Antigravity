import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    idx = 1
    s = []
    for i in range(n):
        s.append(int(data[idx]))
        idx += 1
    
    f = []
    for i in range(n):
        f.append(int(data[idx]))
        idx += 1
    
    # Create list of (start, finish) tuples
    meetings = list(zip(s, f))
    
    # Sort by finish time, if tie then by start time
    meetings.sort(key=lambda x: (x[1], x[0]))
    
    count = 0
    current_end = -1
    
    for start, finish in meetings:
        if start > current_end:
            count += 1
            current_end = finish
    
    print(count)

if __name__ == "__main__":
    main()
