import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    suffix_sums = []
    running_sum = 0
    
    for i in range(n-1, -1, -1):
        running_sum += arr[i]
        suffix_sums.append(running_sum)
    
    suffix_sums.reverse()
    
    print(' '.join(map(str, suffix_sums)))

if __name__ == "__main__":
    main()
