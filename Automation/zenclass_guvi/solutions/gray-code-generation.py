import sys
import re

def main():
    data = sys.stdin.read()
    nums = re.findall(r'-?\d+', data)
    if not nums:
        return
    n = int(nums[0])
    if n < 0:
        print('[]')
        return
    res = [i ^ (i >> 1) for i in range(1 << n)]
    print('[' + ','.join(map(str, res)) + ']')

if __name__ == '__main__':
    main()
