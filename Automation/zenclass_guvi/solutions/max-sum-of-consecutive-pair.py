import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    if len(data) < 2:
        print(-1)
        return
    
    arr = list(map(int, data[1:1+n]))
    
    if n < 2:
        print(-1)
        return
    
    max_sum = float('-inf')
    for i in range(len(arr) - 1):
        current_sum = arr[i] + arr[i + 1]
        if current_sum > max_sum:
            max_sum = current_sum
    
    print(max_sum)

if __name__ == "__main__":
    main()
