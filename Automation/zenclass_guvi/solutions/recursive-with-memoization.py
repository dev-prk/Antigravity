import sys

def main():
    # Read the input
    input_line = sys.stdin.readline().strip()
    
    # Extract the value of n from the input
    if '=' in input_line:
        n = int(input_line.split('=')[1])
    else:
        n = 0  # default case, although problem states valid input
    
    # Handle negative numbers
    if n < 0:
        print(-1)
        return
    
    # Memoized recursive Fibonacci
    memo = {}
    
    def fibonacci(x):
        if x in memo:
            return memo[x]
        if x == 0:
            return 0
        elif x == 1:
            return 1
        else:
            res = fibonacci(x-1) + fibonacci(x-2)
            memo[x] = res
            return res
    
    result = fibonacci(n)
    print(result)

if __name__ == "__main__":
    main()
