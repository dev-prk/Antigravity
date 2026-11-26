import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("no")
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0:
        print("no")
        return
    
    intervals = []
    idx = 2
    for i in range(n):
        a = int(data[idx])
        b = int(data[idx + 1])
        idx += 2
        left = min(a, b)
        right = max(a, b)
        intervals.append((left, right))
    
    intervals.sort()
    
    merged = []
    for interval in intervals:
        if not merged:
            merged.append(interval)
        else:
            last_left, last_right = merged[-1]
            curr_left, curr_right = interval
            if curr_left <= last_right:
                new_right = max(last_right, curr_right)
                merged[-1] = (last_left, new_right)
            else:
                merged.append(interval)
    
    for left, right in merged:
        if left <= m <= right:
            print("yes")
            return
    
    print("no")

if __name__ == "__main__":
    main()
