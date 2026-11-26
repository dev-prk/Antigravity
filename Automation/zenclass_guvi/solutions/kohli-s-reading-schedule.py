import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    t = int(data[1])
    
    if n == 0:
        print(-1)
        return
    
    a = list(map(int, data[2:2+n]))
    
    total_reading = 0
    for i in range(n):
        free_time = 86400 - a[i]
        total_reading += free_time
        if total_reading >= t:
            print(i + 1)
            return
    
    print(-1)

if __name__ == "__main__":
    main()
