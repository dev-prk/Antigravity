import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n <= 0 or n >= 100:
        print(0)
        return
    
    if len(data) < n + 1:
        print(0)
        return
    
    numbers = list(map(int, data[1:n+1]))
    
    total = sum(num for num in numbers if num % 2 == 0)
    print(total)

if __name__ == "__main__":
    main()
