import sys

def generate_gray_code(n):
    if n == 0:
        return ['']
    
    # Start with base case
    result = ['0', '1']
    
    # Build up from 1 bit to n bits
    for i in range(2, n + 1):
        # Create mirror of current sequence
        mirror = result[::-1]
        
        # Prepend '0' to original sequence
        for j in range(len(result)):
            result[j] = '0' + result[j]
        
        # Prepend '1' to mirrored sequence and append
        for j in range(len(mirror)):
            result.append('1' + mirror[j])
    
    return result

def main():
    n = int(sys.stdin.readline().strip())
    gray_codes = generate_gray_code(n)
    print(' '.join(gray_codes))

if __name__ == "__main__":
    main()
