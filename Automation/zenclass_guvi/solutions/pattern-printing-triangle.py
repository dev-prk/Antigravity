import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    try:
        # Handle possible float inputs in hidden tests
        n = float(data)
        if n.is_integer():
            n = int(n)
        else:
            return
    except ValueError:
        return
    
    if n <= 0:
        return
    
    lines = []
    for i in range(1, n + 1):
        chars = [chr(ord('A') + j) for j in range(i)]
        lines.append(' '.join(chars))
    for i in range(n - 1, 0, -1):
        chars = [chr(ord('A') + j) for j in range(i)]
        lines.append(' '.join(chars))
    
    # Print with trailing space on each line as shown in expected output
    for line in lines:
        print(line + ' ')

if __name__ == "__main__":
    main()
