import sys, math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    N = int(data[0])
    K = int(data[1])
    if K < 0 or K > N:
        result = 0
    else:
        result = math.factorial(N) // math.factorial(N - K)
    print(result)

if __name__ == "__main__":
    main()
