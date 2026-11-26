import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n <= 0 or m <= 0:
        print(0)
        return
    
    numbers = list(map(int, data[2:2 + n * m]))
    
    total = 0
    for i in range(n):
        for j in range(m):
            if (i + j) % 2 == 0:
                total += numbers[i * m + j]
    
    print(total)

if __name__ == "__main__":
    main()
