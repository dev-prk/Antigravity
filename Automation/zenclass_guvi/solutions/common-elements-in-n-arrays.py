import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0 or k == 0:
        print(-1)
        return
    
    index = 2
    first_array = list(map(int, data[index:index + k]))
    index += k
    
    common_set = set(first_array)
    
    for i in range(1, n):
        if index >= len(data):
            break
        current_array = list(map(int, data[index:index + k]))
        index += k
        common_set = common_set.intersection(set(current_array))
    
    if not common_set:
        print(-1)
    else:
        common_list = sorted(list(common_set))
        print(' '.join(map(str, common_list)))

if __name__ == "__main__":
    main()
