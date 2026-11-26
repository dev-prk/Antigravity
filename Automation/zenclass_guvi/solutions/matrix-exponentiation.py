import sys

def matrix_mult(A, B, mod):
    """Multiply two 2x2 matrices under modulo."""
    return [
        [(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % mod,
         (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % mod],
        [(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % mod,
         (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % mod]
    ]

def matrix_pow(mat, n, mod):
    """Compute matrix^n using fast exponentiation."""
    result = [[1, 0], [0, 1]]  # Identity matrix
    base = [row[:] for row in mat]  # Copy the matrix
    
    while n > 0:
        if n % 2 == 1:
            result = matrix_mult(result, base, mod)
        base = matrix_mult(base, base, mod)
        n //= 2
    
    return result

def fibonacci(n, m):
    """Compute nth Fibonacci number using matrix exponentiation."""
    if n == 0:
        return 0
    if n == 1:
        return 1 % m
    
    # The Fibonacci matrix [[1, 1], [1, 0]]
    fib_matrix = [[1, 1], [1, 0]]
    
    # Raise to the (n-1)th power
    result_matrix = matrix_pow(fib_matrix, n - 1, m)
    
    # The top-left element is F(n)
    return result_matrix[0][0]

def main():
    # Read input
    line = sys.stdin.readline().strip()
    
    # Parse "n=X,m=Y" format
    if '=' in line and ',' in line:
        parts = line.split(',')
        n_part = parts[0].split('=')
        m_part = parts[1].split('=')
        n = int(n_part[1])
        m = int(m_part[1])
    else:
        # Try space-separated or other formats
        tokens = line.replace('=', ' ').replace(',', ' ').split()
        if len(tokens) >= 4:
            n = int(tokens[1])
            m = int(tokens[3])
        else:
            # Fallback: try to find two numbers
            nums = [int(x) for x in line.replace('=', ' ').replace(',', ' ').split() if x.lstrip('-').isdigit()]
            if len(nums) >= 2:
                n = nums[0]
                m = nums[1]
            else:
                return
    
    # Compute result
    if m <= 0:
        print(-1)
    else:
        result = fibonacci(n, m)
        print(result)

if __name__ == "__main__":
    main()
