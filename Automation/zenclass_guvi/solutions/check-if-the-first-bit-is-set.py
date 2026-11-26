import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    
    if n & (1 << k):
        print("true")
    else:
        print("false")

if __name__ == "__main__":
    main()
