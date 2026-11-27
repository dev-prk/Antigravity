import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    target = n // 2
    count_odd = sum(1 for x in arr if x % 2 != 0)
    if count_odd == target:
        sys.stdout.write('0')
    elif count_odd > target:
        sys.stdout.write(str((count_odd - target) * 2))
    else:
        sys.stdout.write(str((target - count_odd) * 1))

if __name__ == "__main__":
    main()
