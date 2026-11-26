import sys
import ast

def electronics_products(products):
    return [(p['name'], p['category']) for p in products if p['category'] == 'Electronics']

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print([])
        return
    products = ast.literal_eval(line)
    result = electronics_products(products)
    print(result)

if __name__ == "__main__":
    main()
