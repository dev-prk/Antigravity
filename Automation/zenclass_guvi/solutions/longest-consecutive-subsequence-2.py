import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    num_set = set(arr)
    max_length = 0
    
    for num in num_set:
        if num - 1 not in num_set:
            current_num = num
            current_length = 1
            
            while current_num + 1 in num_set:
                current_num += 1
                current_length += 1
            
            max_length = max(max_length, current_length)
    
    print(max_length)

if __name__ == "__main__":
    main()
