import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('no')
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0:
        print('no')
        return
    
    nums = list(map(int, data[2:2+n]))
    
    seen = set()
    for num in nums:
        complement = k - num
        if complement in seen:
            print('yes')
            return
        seen.add(num)
    
    print('no')

if __name__ == "__main__":
    main()
