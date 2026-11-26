import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    prices = list(map(int, data[1:1 + n]))
    
    if n == 0:
        return
    
    min_index = 0
    for i in range(1, n):
        if prices[i] < prices[min_index]:
            min_index = i
    
    print(f"Dealer{min_index}")

if __name__ == "__main__":
    main()
