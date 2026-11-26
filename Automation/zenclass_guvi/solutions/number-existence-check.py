import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('no')
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0:
        print('no')
        return
    
    if len(data) < 2 + n:
        print('no')
        return
    
    arr = list(map(int, data[2:2+n]))
    
    if k in arr:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
