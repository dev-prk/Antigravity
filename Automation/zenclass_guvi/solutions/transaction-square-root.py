import sys
import math

def transaction_sqrt(transaction_amount):
    return math.sqrt(transaction_amount)

if __name__ == "__main__":
    transaction_amount = float(sys.stdin.read().strip())
    result = transaction_sqrt(transaction_amount)
    print(result)
