import sys

def calculate(operation, num1, num2):
    return operation(num1, num2)

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    parts = [p.strip() for p in data.split(',')]
    if len(parts) < 3:
        return
    op_name, a_str, b_str = parts[0], parts[1], parts[2]
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        return

    ops = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else float('inf')
    }

    operation = ops.get(op_name.lower())
    if operation is None:
        return

    result = calculate(operation, a, b)
    # Ensure consistent float formatting
    print(result)

if __name__ == "__main__":
    main()
