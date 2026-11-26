import sys

def main():
    line = sys.stdin.readline()
    if not line:
        print(-1)
        return
    
    line = line.rstrip('\n')
    if not line:
        print(-1)
        return
    
    space_idx = line.rfind(' ')
    if space_idx == -1:
        print(-1)
        return
    
    s = line[:space_idx]
    k = line[space_idx + 1:]
    
    if not k:
        print(-1)
        return
    
    char = k[0]
    
    for i in range(len(s)):
        if s[i] == char:
            print(i + 1)
            return
    
    print(-1)

if __name__ == "__main__":
    main()
