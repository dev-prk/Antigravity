import sys

def main():
    # The four numbers (sum of cubes of their digits) are 153, 370, 371, 407
    # X is the largest: 407
    X = 407
    
    data = sys.stdin.read().strip().split()
    if not data:
        print(X)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(X)
        return
    
    numbers = list(map(int, data[1:n+1]))
    
    # Use a set to track occupied chains
    occupied = set()
    
    for num in numbers:
        chain_index = num % X
        occupied.add(chain_index)
    
    # Number of empty chains
    empty_chains = X - len(occupied)
    print(empty_chains)

if __name__ == "__main__":
    main()
