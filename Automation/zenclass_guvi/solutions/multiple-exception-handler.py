try:
    x = int(input())
    y = int(input())
    result = x // y
    print(result)
except ValueError:
    print("Error: Invalid number format")
except ZeroDivisionError:
    print("Error: Division by zero not allowed")
