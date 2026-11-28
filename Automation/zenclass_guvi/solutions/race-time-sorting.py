import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("")
        print(-1)
        return
    
    times = list(map(int, data[1:n+1]))
    times.sort()
    
    sorted_str = ' '.join(map(str, times)) + ' '
    print(sorted_str)
    print(times[0])

if __name__ == "__main__":
    main()
