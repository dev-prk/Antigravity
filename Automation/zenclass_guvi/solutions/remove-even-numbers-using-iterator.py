import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("")
        return
    
    numbers = list(map(int, data[1:n+1]))
    
    result = [x for x in numbers if x % 2 != 0]
    
    print(" ".join(map(str, result)))

if __name__ == "__main__":
    main()
