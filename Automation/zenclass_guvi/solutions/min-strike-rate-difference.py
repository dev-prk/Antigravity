import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n < 2:
        return
    
    strike_rates = []
    for i in range(1, n + 1):
        strike_rates.append(float(data[i]))
    
    min_diff = float('inf')
    result = (0, 0)
    
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = abs(strike_rates[j] - strike_rates[i])
            if diff < min_diff:
                min_diff = diff
                result = (strike_rates[i], strike_rates[j])
    
    print(f"{result[0]} {result[1]}")

if __name__ == "__main__":
    main()
