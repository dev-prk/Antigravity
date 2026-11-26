import sys

def sigma(n):
    if n <= 0:
        return 0
    total = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    # Parse n from input like "n=6"
    try:
        # Look for the value after '='
        if '=' in data:
            val_str = data.split('=', 1)[1].strip()
            n = int(val_str)
        else:
            n = int(data.strip())
    except ValueError:
        return
    result = sigma(n)
    print(result)

if __name__ == "__main__":
    main()
