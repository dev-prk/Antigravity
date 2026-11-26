import sys

class Item:
    def __init__(self, title, price):
        self.title = title
        self.price = price
    
    def change_price(self, new_price):
        self.price = new_price

class Book(Item):
    def __init__(self, title, author, price):
        super().__init__(title, price)
        self.author = author
    
    def print_details(self):
        print(f"Book: {self.title} by {self.author}, priced at ${self.price}")

class Magazine(Item):
    def __init__(self, title, price, issue_number):
        super().__init__(title, price)
        self.issue_number = issue_number
    
    def print_details(self):
        print(f"Magazine: {self.title}, Issue No. {self.issue_number}, priced at ${self.price}")

lines = [line.strip() for line in sys.stdin if line.strip()]

if len(lines) >= 4:
    parts = lines[0].split(', ')
    book = Book(parts[0], parts[1], float(parts[2]))
    book.print_details()
    
    parts = lines[1].split(', ')
    magazine = Magazine(parts[0], float(parts[1]), int(parts[2]))
    magazine.print_details()
    
    book.change_price(float(lines[2]))
    book.print_details()
    
    magazine.change_price(float(lines[3]))
    magazine.print_details()
