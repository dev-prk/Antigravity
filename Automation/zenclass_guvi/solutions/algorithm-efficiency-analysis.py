import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    ops = int(data[0])
    mem = int(data[1])
    total = ops + mem
    diff = ops - mem
    product = ops * mem
    efficiency = ops // mem
    print(f"Total Usage: {total}")
    print(f"Difference: {diff}")
    print(f"Product: {product}")
    print(f"Efficiency Score: {efficiency}")

if __name__ == "__main__":
    main()
