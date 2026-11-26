import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    accounts = {}
    
    for _ in range(n):
        acc_num = int(data[idx])
        idx += 1
        holder_name = data[idx]
        idx += 1
        balance = int(data[idx])
        idx += 1
        accounts[acc_num] = {
            'holder_name': holder_name,
            'balance': balance
        }
    
    sender = int(data[idx])
    idx += 1
    receiver = int(data[idx])
    idx += 1
    amount = int(data[idx])
    idx += 1
    
    if amount <= 0:
        print("Transfer failed")
        return
    
    if sender not in accounts or receiver not in accounts:
        print("Account not found")
        return
    
    if accounts[sender]['balance'] < amount:
        print("Insufficient balance")
        return
    
    accounts[sender]['balance'] -= amount
    accounts[receiver]['balance'] += amount
    
    print("Transfer successful")

if __name__ == "__main__":
    main()
