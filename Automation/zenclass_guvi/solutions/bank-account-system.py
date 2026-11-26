import sys

class BankAccount:
    def __init__(self, accountNumber, balance):
        self.accountNumber = accountNumber
        self.balance = balance
    
    def deposit(self, amount):
        self.balance += amount
    
    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient Balance")
        else:
            self.balance -= amount
            print(float(self.balance))

def main():
    lines = sys.stdin.read().strip().split('\n')
    accountNumber = int(lines[0])
    balance = int(lines[1])
    account = BankAccount(accountNumber, balance)
    
    index = 2
    while index < len(lines):
        operation = lines[index]
        if operation in ['deposit', 'withdraw'] and index + 1 < len(lines):
            amount = int(lines[index + 1])
            if operation == 'deposit':
                account.deposit(amount)
            elif operation == 'withdraw':
                account.withdraw(amount)
            index += 2
        else:
            index += 1

if __name__ == "__main__":
    main()
