import sys

class Calculator:
    @staticmethod
    def add(num1, num2):
        return num1 + num2
    
    @staticmethod
    def subtract(num1, num2):
        return num1 - num2
    
    @staticmethod
    def multiply(num1, num2):
        return num1 * num2
    
    @staticmethod
    def divide(num1, num2):
        return num1 / num2

if __name__ == "__main__":
    line = sys.stdin.readline().strip()
    if line.startswith("Calculator."):
        parts = line.split("(")
        method_part = parts[0].replace("Calculator.", "")
        args_part = parts[1].rstrip(")").split(",")
        num1 = float(args_part[0].strip())
        num2 = float(args_part[1].strip())
        if method_part == "add":
            result = Calculator.add(num1, num2)
        elif method_part == "subtract":
            result = Calculator.subtract(num1, num2)
        elif method_part == "multiply":
            result = Calculator.multiply(num1, num2)
        elif method_part == "divide":
            result = Calculator.divide(num1, num2)
        if result == int(result):
            print(int(result))
        else:
            print(result)
