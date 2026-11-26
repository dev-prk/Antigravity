import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1+n]))
    
    first_index = {}
    best_i = None
    best_val = None
    
    for idx, val in enumerate(nums):
        if val in first_index:
            i = first_index[val]
            if best_i is None or i < best_i:
                best_i = i
                best_val = val
        else:
            first_index[val] = idx
    
    if best_i is None:
        print('unique')
    else:
        print(best_val)

if __name__ == "__main__":
    main()
