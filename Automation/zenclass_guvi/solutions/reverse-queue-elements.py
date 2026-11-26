import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    # Take exactly n numbers after the first token
    nums = data[1:1 + n]
    # Reverse the list
    reversed_nums = nums[::-1]
    # Output space-separated
    sys.stdout.write(' '.join(reversed_nums))

if __name__ == "__main__":
    main()
