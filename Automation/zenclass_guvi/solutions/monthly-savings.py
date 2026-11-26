import sys

def main():
    n = int(sys.stdin.readline().strip())
    
    if n == 0:
        print(1000)
        return
    
    if n == 1:
        print(2000)
        return
    
    prev2 = 1000
    prev1 = 1000
    total = prev2 + prev1
    
    for i in range(2, n + 1):
        current = prev1 + prev2
        total += current
        prev2 = prev1
        prev1 = current
    
    print(total)

if __name__ == "__main__":
    main()
