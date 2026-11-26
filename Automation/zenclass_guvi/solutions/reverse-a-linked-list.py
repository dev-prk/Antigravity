import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("")
        return
    
    values = list(map(int, data[1:n+1]))
    values.reverse()
    print(' '.join(map(str, values)))

if __name__ == "__main__":
    main()
