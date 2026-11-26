import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0:
        print("Bon Appetit")
        return
    
    costs = list(map(int, data[2:2+n]))
    b_charged = int(data[2+n])
    
    # Calculate total cost excluding the k-th item
    total = sum(costs) - costs[k]
    
    # Anna's fair share
    anna_share = total // 2
    
    # Calculate difference
    refund = b_charged - anna_share
    
    if refund == 0:
        print("Bon Appetit")
    else:
        print(refund)

if __name__ == "__main__":
    main()
