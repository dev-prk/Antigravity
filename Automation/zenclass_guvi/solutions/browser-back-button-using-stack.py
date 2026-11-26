import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("No Previous Page")
        return
    
    pages = list(map(int, data[1:1+n]))
    
    if n == 1:
        print("No Previous Page")
    else:
        print("Current Page After Back:", pages[n-2])

if __name__ == "__main__":
    main()
