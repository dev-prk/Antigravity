def product_stock(products):
    result = {}
    for product in products:
        name = product['name']
        stock = product['stock']
        result[name] = result.get(name, 0) + stock
    return result

# Read input from sys.stdin and execute
import sys

if __name__ == "__main__":
    products_input = sys.stdin.read().strip()
    if products_input:
        products = eval(products_input)
        result = product_stock(products)
        print(result)
    else:
        print({})
