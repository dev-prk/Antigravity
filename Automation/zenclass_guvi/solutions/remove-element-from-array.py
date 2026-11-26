import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('empty')
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0 or len(data) < 2 + n:
        print('empty')
        return
    
    arr = list(map(int, data[2:2+n]))
    
    result = [x for x in arr if x != k]
    
    if not result:
        print('empty')
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
