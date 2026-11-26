import sys

def main():
    celsius = float(sys.stdin.readline().strip())
    fahrenheit = celsius * 9/5 + 32
    if fahrenheit == int(fahrenheit):
        print(int(fahrenheit))
    else:
        print(round(fahrenheit, 1))

if __name__ == "__main__":
    main()
