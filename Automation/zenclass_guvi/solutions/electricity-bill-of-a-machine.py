import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    units = int(data[0])
    price = float(data[1])
    total = units * price
    # Print with exactly two decimal places
    print("{:.2f}".format(total))

if __name__ == "__main__":
    main()
