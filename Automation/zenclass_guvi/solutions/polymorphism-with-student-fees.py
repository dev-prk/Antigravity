import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    credits = int(data)
    undergraduate_fee = 5000
    graduate_fee = credits * 50
    print(undergraduate_fee)
    print(graduate_fee)

if __name__ == "__main__":
    main()
