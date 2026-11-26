import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('no')
        return
    
    n = int(data[0])
    
    if n == 0:
        print('yes')
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if len(arr) <= 1:
        print('yes')
        return
    
    ascending = True
    descending = True
    
    for i in range(len(arr) - 1):
        if arr[i] > arr[i + 1]:
            ascending = False
        if arr[i] < arr[i + 1]:
            descending = False
    
    if ascending or descending:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
