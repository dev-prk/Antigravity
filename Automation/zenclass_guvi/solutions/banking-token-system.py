import sys

def main():
    lines = [line.strip() for line in sys.stdin if line.strip()]
    if not lines:
        return
    
    n = int(lines[0])
    accounts = []
    for i in range(1, n + 1):
        parts = lines[i].split()
        acc_num = int(parts[0])
        name = parts[1]
        balance = int(parts[2])
        accounts.append((acc_num, name, balance))
    
    operation_line = lines[n + 1]
    op_parts = operation_line.split()
    choice = int(op_parts[0])
    
    if choice == 1:
        acc_num = int(op_parts[1])
        amount = int(op_parts[2])
        for i in range(len(accounts)):
            if accounts[i][0] == acc_num:
                old_balance = accounts[i][2]
                new_balance = old_balance - amount
                accounts[i] = (acc_num, accounts[i][1], new_balance)
                break
    elif choice == 2:
        acc_num = int(op_parts[1])
        amount = int(op_parts[2])
        for i in range(len(accounts)):
            if accounts[i][0] == acc_num:
                old_balance = accounts[i][2]
                new_balance = old_balance + amount
                accounts[i] = (acc_num, accounts[i][1], new_balance)
                break
    elif choice == 3:
        from_acc = int(op_parts[1])
        to_acc = int(op_parts[2])
        amount = int(op_parts[3])
        for i in range(len(accounts)):
            if accounts[i][0] == from_acc:
                new_balance = accounts[i][2] - amount
                accounts[i] = (from_acc, accounts[i][1], new_balance)
            if accounts[i][0] == to_acc:
                accounts[i] = (to_acc, accounts[i][1], accounts[i][2] + amount)
    
    for acc in accounts:
        if isinstance(acc[2], float):
            print(f"{acc[0]} {acc[1]} {acc[2]}")
        else:
            print(f"{acc[0]} {acc[1]} {acc[2]}")

if __name__ == "__main__":
    main()
