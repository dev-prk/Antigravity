import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    line = line.rstrip('\n')
    if not line:
        print(-1)
        return
    
    parts = line.rsplit(' ', 1)
    if len(parts) < 2:
        print(-1)
        return
    
    s = parts[0].rstrip(' ')
    k = parts[1]
    
    if not s or not k:
        print(-1)
        return
    
    count = s.count(k)
    
    if count == 0:
        print(-1)
    else:
        print(count)

if __name__ == "__main__":
    main()
