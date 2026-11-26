def expensive_products(products):
    return [product['name'] for product in products if product['price'] > 50]

import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print([])
        return
    products = eval(line)
    result = expensive_products(products)
    print(result)

if __name__ == "__main__":
    main()
