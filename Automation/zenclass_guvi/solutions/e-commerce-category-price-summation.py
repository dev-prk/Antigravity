import sys
import ast
from math import fsum

def total_price(products, category):
    return fsum(product['price'] for product in products if product['category'] == category)

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    # Find the category part which is the last quoted string
    # Split from the right to find the category
    last_quote = line.rfind("'")
    if last_quote == -1:
        return
    # Find the matching opening quote
    second_last_quote = line[:last_quote].rfind("'")
    if second_last_quote == -1:
        return
    category = line[second_last_quote+1:last_quote]
    # Parse the products list
    products_str = line[:second_last_quote].rstrip()
    products_str = products_str.rstrip(',') if products_str.endswith(',') else products_str
    products = ast.literal_eval(products_str)
    result = total_price(products, category)
    print(result)

if __name__ == "__main__":
    main()
