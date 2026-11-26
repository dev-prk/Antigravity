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
    
    numbers = list(map(int, data[1:n+1]))
    result = []
    
    for i in range(n):
        if i % 2 == 1 and numbers[i] % 2 == 0:  # odd index, even number
            result.append(numbers[i])
        elif i % 2 == 0 and numbers[i] % 2 != 0:  # even index, odd number
            result.append(numbers[i])
    
    if not result:
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
