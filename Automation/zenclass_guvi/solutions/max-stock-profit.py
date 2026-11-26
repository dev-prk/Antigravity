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
    
    prices = list(map(int, data[1:n+1]))
    
    if n == 1:
        print(-1)
        return
    
    min_price = prices[0]
    max_profit = -1
    
    for i in range(1, n):
        if prices[i] < min_price:
            min_price = prices[i]
        else:
            profit = prices[i] - min_price
            if profit > max_profit:
                max_profit = profit
    
    print(max_profit)

if __name__ == "__main__":
    main()
