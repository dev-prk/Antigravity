import sys

class ItemNotFoundError(Exception):
    pass

def get_stock(item: str) -> int:
    stock = {"Apples": 50, "Oranges": 30, "Grapes": 0}
    if item not in stock:
        raise ItemNotFoundError("Item not found")
    return stock[item]

def handle_stock_request(item: str) -> str:
    try:
        stock = get_stock(item)
        if stock > 0:
            return f"Stock for {item}: {stock}"
        else:
            return "Item not found"
    except ItemNotFoundError:
        return "Item not found"

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    item = data
    result = handle_stock_request(item)
    print(result)

main()
