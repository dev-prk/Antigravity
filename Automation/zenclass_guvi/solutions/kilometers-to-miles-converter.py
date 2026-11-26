import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        km = float(data[0])
    except ValueError:
        return
    miles = km * 0.621371
    print(f"{miles:.2f}")

if __name__ == "__main__":
    main()
