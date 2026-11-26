import sys

def get_book_details(isbn: str) -> dict:
    books = {
        "1234567890": {
            'title': 'Python Programming',
            'author': 'John Doe',
            'price': 500,
            'quantity': 10
        },
        "9876543210": {
            'title': 'Data Structures and Algorithms',
            'author': 'Jane Doe',
            'price': 600,
            'quantity': 5
        },
        "1111111111": {
            'title': 'Machine Learning',
            'author': 'Sam Smith',
            'price': 700,
            'quantity': 2
        }
    }
    if isbn in books:
        return books[isbn]
    raise ValueError("Book not found")

def handle_book_request(isbn: str) -> str:
    try:
        details = get_book_details(isbn)
        return f"Book found: {details['title']} by {details['author']}. Price: {details['price']}, Quantity: {details['quantity']}"
    except ValueError:
        return "Book not found"

if __name__ == "__main__":
    isbn = sys.stdin.read().strip()
    result = handle_book_request(isbn)
    print(result)
