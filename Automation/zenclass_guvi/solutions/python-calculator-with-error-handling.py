def calculate(operation: str, num1: float, num2: float) -> float:
    if operation == 'add':
        return num1 + num2
    elif operation == 'subtract':
        return num1 - num2
    elif operation == 'multiply':
        return num1 * num2
    elif operation == 'divide':
        if num2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return num1 / num2
    else:
        raise ValueError("Invalid operation")

def handle_calculation(operation: str, num1: float, num2: float) -> str:
    try:
        result = calculate(operation, num1, num2)
        return f"Result: {result}"
    except ValueError:
        return "Invalid operation"
    except ZeroDivisionError:
        return "Cannot divide by zero"

if __name__ == "__main__":
    import sys
    line = sys.stdin.readline().strip()
    if line:
        parts = line.split(', ')
        op = parts[0].strip()
        n1 = float(parts[1].strip())
        n2 = float(parts[2].strip())
        print(handle_calculation(op, n1, n2))
