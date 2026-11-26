import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 4:
        print("no")
        return
    
    n = int(data[0])
    a = int(data[1])
    b = int(data[2])
    c = int(data[3])
    
    if n % a == 0 and n % b == 0 and n % c == 0:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
