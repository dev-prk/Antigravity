import sys

def main():
    s = sys.stdin.readline().strip()
    
    if len(s) < 3:
        print(0)
        return
    
    first = s[0]
    middle = s[len(s) // 2]
    last = s[-1]
    
    if (first.lower() == 'a') and (middle.lower() == 'm') and (last.lower() == 'z'):
        print(1)
    else:
        print(0)

if __name__ == "__main__":
    main()
