import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    if len(data) < 2:
        print(-1)
        return
    
    numbers = list(map(int, data[1:n+1]))
    
    # Handle case where we don't have enough valid numbers
    if len(set(numbers)) < 2:
        print(-1)
        return
    
    # Find second smallest element
    unique_numbers = sorted(set(numbers))
    
    if len(unique_numbers) < 2:
        print(-1)
    else:
        print(unique_numbers[1])

if __name__ == "__main__":
    main()
