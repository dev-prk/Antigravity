import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0 or k == 0:
        print(0)
        return
    
    prices = list(map(int, data[2:2+n]))
    prices.sort()
    
    count = 0
    total = 0
    
    for price in prices:
        if total + price <= k:
            total += price
            count += 1
        else:
            break
    
    print(count)

if __name__ == "__main__":
    main()
