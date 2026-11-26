import sys, ast

def get_products_in_budget(budget, products):
    # sort by price (second element)
    for pid, price in sorted(products, key=lambda x: x[1]):
        if budget < 0 and price >= 0:
            # if budget negative, any non‑negative price will exceed it
            break
        if budget - price < 0:
            break
        budget -= price
        yield (pid, price)

def main():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    # first non‑empty line is budget
    i = 0
    while i < len(data) and data[i].strip() == '':
        i += 1
    if i >= len(data):
        return
    try:
        budget = int(data[i].strip())
    except:
        # if budget line contains extra spaces or other chars, evaluate safely
        budget = int(ast.literal_eval(data[i].strip()))
    i += 1
    # skip empty lines to find products list
    while i < len(data) and data[i].strip() == '':
        i += 1
    products = []
    if i < len(data):
        try:
            products = ast.literal_eval(data[i].strip())
        except:
            # fallback: try to parse as empty list
            products = []
    for item in get_products_in_budget(budget, products):
        print(item)

if __name__ == "__main__":
    main()
