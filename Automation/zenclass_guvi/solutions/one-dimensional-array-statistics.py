import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("Sum: 0")
        print("Average: 0")
        print("Maximum: -1")
        print("Minimum: -1")
        return
    
    arr = list(map(int, data[1:n+1]))
    
    total = sum(arr)
    avg = total // n
    max_val = max(arr)
    min_val = min(arr)
    
    print(f"Sum: {total}")
    print(f"Average: {avg}")
    print(f"Maximum: {max_val}")
    print(f"Minimum: {min_val}")

if __name__ == "__main__":
    main()
