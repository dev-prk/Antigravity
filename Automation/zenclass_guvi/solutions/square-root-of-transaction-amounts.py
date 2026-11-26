import math

def calculate_sqrt(transaction_amounts):
    result = []
    for amount in transaction_amounts:
        result.append(math.sqrt(amount))
    return result

if __name__ == "__main__":
    transaction_amounts = eval(input().strip())
    print(calculate_sqrt(transaction_amounts))
