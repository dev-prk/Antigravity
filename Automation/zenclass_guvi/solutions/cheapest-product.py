import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    min_price = float('inf')
    min_name = ""
    idx = 1
    for _ in range(n):
        name = data[idx]
        price = int(data[idx + 1])
        idx += 2
        if price < min_price:
            min_price = price
            min_name = name
    print(f"{min_name} {min_price}")

if __name__ == "__main__":
    main()
