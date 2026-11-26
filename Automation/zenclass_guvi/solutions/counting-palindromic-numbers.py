import sys

def count_palindromic(n):
    if n < 1:
        return 0
    
    s = str(n)
    length = len(s)
    count = 0
    
    for i in range(1, length):
        count += 9 * (10 ** ((i - 1) // 2))
    
    half = (length + 1) // 2
    prefix = int(s[:half])
    first_half = s[:half]
    
    if length % 2 == 0:
        palindrome = int(first_half + first_half[::-1])
    else:
        palindrome = int(first_half + first_half[-2::-1])
    
    if palindrome <= n:
        count += prefix - 10 ** (half - 1) + 1
    else:
        count += prefix - 10 ** (half - 1)
    
    return count

n = int(sys.stdin.readline().strip())
print(count_palindromic(n))
