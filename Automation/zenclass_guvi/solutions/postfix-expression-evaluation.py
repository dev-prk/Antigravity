import sys

def evaluate_postfix(expr):
    stack = []
    operators = {'+', '-', '*', '/'}
    
    for char in expr:
        if char.isdigit():
            stack.append(int(char))
        elif char in operators:
            if len(stack) < 2:
                return -1
            b = stack.pop()
            a = stack.pop()
            
            if char == '+':
                stack.append(a + b)
            elif char == '-':
                stack.append(a - b)
            elif char == '*':
                stack.append(a * b)
            elif char == '/':
                if b == 0:
                    return -1
                stack.append(a // b)
        else:
            return -1
    
    if len(stack) != 1:
        return -1
    
    return stack[0]

def main():
    expr = sys.stdin.readline().strip()
    
    if not expr:
        print(-1)
        return
    
    result = evaluate_postfix(expr)
    print(result)

if __name__ == "__main__":
    main()
