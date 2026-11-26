import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    count = 0
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i] < arr[j]:
                count += 1
    
    print(count)

if __name__ == "__main__":
    main()
