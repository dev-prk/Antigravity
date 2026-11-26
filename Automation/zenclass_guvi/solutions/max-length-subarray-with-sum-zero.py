import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(-1)
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    
    prefix_sum = 0
    first_index = {0: -1}  # sum -> earliest index
    max_len = 0
    
    for i, val in enumerate(arr):
        prefix_sum += val
        if prefix_sum in first_index:
            length = i - first_index[prefix_sum]
            if length > max_len:
                max_len = length
        else:
            first_index[prefix_sum] = i
    
    print(max_len if max_len > 0 else -1)

if __name__ == "__main__":
    main()
