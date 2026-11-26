import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    if N == 0:
        E = int(data[idx])
        idx += 1
        results = []
        for _ in range(E):
            event_type = int(data[idx])
            if event_type == 3:
                idx += 3
            else:
                idx += 4
        print('\n'.join(map(str, results)) if results else "")
        return
    
    arr = list(map(int, data[idx:idx+N]))
    idx += N
    
    E = int(data[idx])
    idx += 1
    
    for _ in range(E):
        event_type = int(data[idx])
        if event_type == 1:
            x = int(data[idx+1]) - 1
            y = int(data[idx+2]) - 1
            z = int(data[idx+3])
            idx += 4
            for i in range(x, y + 1):
                arr[i] += z
        elif event_type == 2:
            x = int(data[idx+1]) - 1
            y = int(data[idx+2]) - 1
            z = int(data[idx+3])
            idx += 4
            for i in range(x, y + 1):
                arr[i] = max(0, arr[i] - z)
        elif event_type == 3:
            x = int(data[idx+1]) - 1
            y = int(data[idx+2]) - 1
            idx += 3
            total = sum(arr[x:y+1])
            print(total)

if __name__ == "__main__":
    main()
