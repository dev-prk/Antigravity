import sys
import ast

def unique_brands(products):
    return {p['brand'] for p in products}

if __name__ == "__main__":
    products = ast.literal_eval(sys.stdin.read().strip())
    brands = unique_brands(products)
    print(sorted(brands))
