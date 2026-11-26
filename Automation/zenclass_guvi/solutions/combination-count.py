import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    N = int(data[0])
    K = int(data[1])
    
    if K == 0:
        print(1)
        return
    
    result = 1
    for i in range(N, N - K, -1):
        result *= i
    
    print(result)

if __name__ == "__main__":
    main()
