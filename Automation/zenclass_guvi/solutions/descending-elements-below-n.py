import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    elements = list(map(int, data[1:1+n]))
    
    # Filter elements less than n
    filtered = [x for x in elements if x < n]
    
    if not filtered:
        print(-1)
    else:
        filtered.sort(reverse=True)
        print(' '.join(map(str, filtered)))

if __name__ == "__main__":
    main()
