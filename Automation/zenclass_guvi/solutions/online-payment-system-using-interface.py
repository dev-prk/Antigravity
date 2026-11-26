from abc import ABC, abstractmethod

class Payment(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class UPIPayment(Payment):
    def pay(self, amount):
        print("Payment Successful")
        print(f"Amount Paid: {amount}")

if __name__ == "__main__":
    amount = int(input())
    upi_payment = UPIPayment()
    upi_payment.pay(amount)
