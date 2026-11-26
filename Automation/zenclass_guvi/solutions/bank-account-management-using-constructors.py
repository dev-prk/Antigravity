import sys

class BankAccount:
    def __init__(self, acc_num, holder_name, balance):
        self.account_number = acc_num
        self.account_holder = holder_name
        self.balance = balance
    
    def display_account_number(self):
        print(f"Account Number: {self.account_number}")
    
    def display_account_holder(self):
        print(f"Account Holder: {self.account_holder}")
    
    def display_balance(self):
        print(f"Balance: {self.balance}")
    
    def add_bonus(self):
        self.balance += 1000
        print(f"Balance After Bonus: {self.balance}")

def main():
    lines = sys.stdin.read().strip().split('\n')
    acc_num = int(lines[0])
    holder_name = lines[1]
    balance = int(lines[2])
    
    account = BankAccount(acc_num, holder_name, balance)
    account.display_account_number()
    account.display_account_holder()
    account.display_balance()
    account.add_bonus()

if __name__ == "__main__":
    main()
