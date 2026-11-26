import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split()
    start = int(parts[0])
    end = int(parts[1])
    
    if start <= end:
        result = list(range(start, end + 1))
    else:
        result = list(range(start, end - 1, -1))
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
