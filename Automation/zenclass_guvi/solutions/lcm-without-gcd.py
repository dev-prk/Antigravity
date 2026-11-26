import sys

def lcm(a, b):
    result = max(a, b)
    while result % a != 0 or result % b != 0:
        result += 1
    return result

def lcm_of_list(numbers):
    if not numbers:
        return 0
    result = numbers[0]
    for i in range(1, len(numbers)):
        result = lcm(result, numbers[i])
    return result

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    numbers = list(map(int, data[1:n+1]))
    if not numbers:
        print(0)
        return
    result = lcm_of_list(numbers)
    print(result)

if __name__ == "__main__":
    main()
