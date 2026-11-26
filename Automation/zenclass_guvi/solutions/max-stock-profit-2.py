import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    prices = list(map(int, data[1:n+1]))
    
    if len(prices) < 2:
        print(0)
        return
    
    min_price = prices[0]
    max_profit = 0
    
    for i in range(1, len(prices)):
        current_price = prices[i]
        profit = current_price - min_price
        if profit > max_profit:
            max_profit = profit
        if current_price < min_price:
            min_price = current_price
    
    print(max(max_profit, 0))

if __name__ == "__main__":
    main()
