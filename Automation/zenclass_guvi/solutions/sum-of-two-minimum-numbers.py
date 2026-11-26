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
    
    digits = list(map(int, data[1:n+1]))
    digits.sort()
    
    num1 = 0
    num2 = 0
    
    for i in range(len(digits)):
        if i % 2 == 0:
            num1 = num1 * 10 + digits[i]
        else:
            num2 = num2 * 10 + digits[i]
    
    print(num1 + num2)

if __name__ == "__main__":
    main()
