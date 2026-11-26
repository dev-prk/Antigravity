import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("no")
        return
    
    n = int(data[0])
    
    if n == 0:
        print("yes")
        return
    
    a = list(map(int, data[1:1+n]))
    b = list(map(int, data[1+n:1+2*n]))
    
    sum_a = sum(a)
    sum_b = sum(b)
    
    diff = sum_a - sum_b
    
    if diff % 2 != 0:
        print("no")
        return
    
    target = diff // 2
    
    b_set = set(b)
    
    for val in a:
        needed = val - target
        if needed in b_set:
            print("yes")
            return
    
    print("no")

if __name__ == "__main__":
    main()
