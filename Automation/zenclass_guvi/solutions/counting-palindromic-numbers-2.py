import sys

def count_palindromes(n):
    if n < 1:
        return 0
    
    count = 0
    for i in range(1, n + 1):
        s = str(i)
        if s == s[::-1]:
            count += 1
    return count

def main():
    n = int(sys.stdin.readline().strip())
    print(count_palindromes(n))

if __name__ == "__main__":
    main()
