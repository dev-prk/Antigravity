import sys

def main():
    data = sys.stdin.read().splitlines()
    s1 = data[0].rstrip('\n') if len(data) > 0 else ''
    s2 = data[1].rstrip('\n') if len(data) > 1 else ''
    
    idx = s2.find(s1)
    if idx != -1:
        print(idx + 1)
        return
        
    idx = s1.find(s2)
    if idx != -1:
        print(idx + 1)
        return
        
    print(-1)

if __name__ == "__main__":
    main()
