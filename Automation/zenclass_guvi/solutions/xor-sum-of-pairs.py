def main():
    import sys
    n = int(sys.stdin.readline().strip())
    arr = list(map(int, sys.stdin.readline().split()))
    
    total = 0
    for bit in range(31):
        count = 0
        for num in arr:
            if (num >> bit) & 1:
                count += 1
        pairs = count * (n - count)
        total += pairs * (1 << bit)
    
    print(total)

if __name__ == "__main__":
    main()
