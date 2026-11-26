import sys
from functools import cmp_to_key

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    
    nums = data[1:n+1]
    
    def compare(x, y):
        if x + y > y + x:
            return -1
        elif x + y < y + x:
            return 1
        else:
            return 0
    
    nums.sort(key=cmp_to_key(compare))
    
    result = ''.join(nums)
    
    if result[0] == '0':
        print(0)
    else:
        print(result)

if __name__ == "__main__":
    main()
