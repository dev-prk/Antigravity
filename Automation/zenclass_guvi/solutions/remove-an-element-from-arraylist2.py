import sys

def main():
    data = sys.stdin.read().strip().split()
    n = int(data[0])
    elements = list(map(int, data[1:1+n]))
    target = int(data[1+n])
    
    elements.remove(target)
    print(' '.join(map(str, elements)))

if __name__ == "__main__":
    main()
