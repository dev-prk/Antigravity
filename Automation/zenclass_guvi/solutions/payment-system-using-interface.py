import sys
from abc import ABC, abstractmethod

class Payment(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class UPI(Payment):
    def pay(self, amount):
        print(f"UPI Payment: {amount}")

class Card(Payment):
    def pay(self, amount):
        print(f"Card Payment: {amount}")

class Cash(Payment):
    def pay(self, amount):
        print(f"Cash Payment: {amount}")

def main():
    method = sys.stdin.readline().strip().lower()
    amount = int(sys.stdin.readline().strip())
    
    if method == "upi":
        payment = UPI()
    elif method == "card":
        payment = Card()
    elif method == "cash":
        payment = Cash()
    else:
        return
    
    payment.pay(amount)

if __name__ == "__main__":
    main()
