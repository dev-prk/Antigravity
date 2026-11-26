def get_product_details(product_id: str) -> dict:
    products = {
        "123456": {"name": "Wireless Mouse", "category": "Electronics", "price": 500, "stock": 10},
        "789012": {"name": "Running Shoes", "category": "Sports", "price": 600, "stock": 5},
        "345678": {"name": "Coffee Maker", "category": "Home Appliances", "price": 700, "stock": 2}
    }
    if product_id not in products:
        raise Exception("Product not found")
    return products[product_id]

def handle_product_request(product_id: str) -> str:
    try:
        details = get_product_details(product_id)
        return f"Product found: {details['name']}, Category: {details['category']}, Price: {details['price']}, Stock: {details['stock']}"
    except Exception as e:
        return str(e)
    finally:
        print("Request handled")

import sys
product_id = sys.stdin.read().strip()
result = handle_product_request(product_id)
print(result)
