import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    m = int(data[0])
    k = int(data[1])
    nums = [str(i) for i in range(m + 1, k)]
    sys.stdout.write(' '.join(nums) + '\n')

if __name__ == '__main__':
    main()
