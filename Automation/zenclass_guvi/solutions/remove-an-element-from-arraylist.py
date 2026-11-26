import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    elements = list(map(int, data[1:1+n]))
    target = int(data[1+n])
    
    result = [x for x in elements if x != target]
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
