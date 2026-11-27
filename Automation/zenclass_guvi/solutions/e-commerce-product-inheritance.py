import sys

class Product:
    def __init__(self, name, price, seller):
        self.name = name
        self.price = price
        self.seller = seller
    
    def print_details(self):
        pass

class NewProduct(Product):
    def print_details(self):
        # Format price to always show 2 decimal places
        formatted_price = f"{self.price:.2f}"
        print(f"New Product: {self.name}, Price: ${formatted_price}, Seller: {self.seller}")

class UsedProduct(Product):
    def __init__(self, name, price, seller, condition):
        super().__init__(name, price, seller)
        self.condition = condition
    
    def print_details(self):
        # Format price to always show 2 decimal places
        formatted_price = f"{self.price:.2f}"
        print(f"Used Product: {self.name}, Price: ${formatted_price}, Seller: {self.seller}, Condition: {self.condition}")

def main():
    lines = sys.stdin.read().strip().split('\n')
    products = []
    
    for line in lines:
        if not line.strip():
            continue
        
        parts = line.split(', ')
        
        if len(parts) == 3:
            # New product
            name, price, seller = parts
            price = float(price)
            product = NewProduct(name, price, seller)
            products.append(product)
        elif len(parts) == 4:
            # Used product
            name, price, seller, condition = parts
            price = float(price)
            product = UsedProduct(name, price, seller, condition)
            products.append(product)
    
    for product in products:
        product.print_details()

if __name__ == "__main__":
    main()
