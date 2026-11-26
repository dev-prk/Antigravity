import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        print(-1)
        return
    
    n = int(data[0])
    k = int(data[1])
    
    count = str(n).count(str(k))
    
    if count == 0:
        print(-1)
    else:
        print(count)

if __name__ == "__main__":
    main()
