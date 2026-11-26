import sys

def solve():
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print(-1)
        return
    
    length = 1
    count = 2
    while n > count:
        n -= count
        length += 1
        count *= 2
    
    numbers = []
    for i in range(length):
        numbers.append(3)
    
    n -= 1
    for i in range(length):
        if n >= (1 << (length - 1 - i)):
            numbers[i] = 4
            n -= (1 << (length - 1 - i))
    
    print(''.join(map(str, numbers)))

if __name__ == "__main__":
    solve()
