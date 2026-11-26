import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0 or len(data) < 2:
        return
    customer_ids = list(map(int, data[1:1+n]))
    print(f"Customer Served: {customer_ids[0]}")

if __name__ == "__main__":
    main()
