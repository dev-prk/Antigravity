import sys

def evaluate_postfix(expression):
    stack = []
    tokens = expression.split()
    
    for token in tokens:
        if token in '+-*/':
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                # Handle integer division towards zero
                stack.append(int(a / b))
        else:
            stack.append(int(token))
    
    return stack[0]

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    result = evaluate_postfix(line)
    print(result)

if __name__ == "__main__":
    main()
