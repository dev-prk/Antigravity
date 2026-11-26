import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    num1 = data[0]
    num2 = data[1]
    print(num1.count(num2))

if __name__ == '__main__':
    main()
