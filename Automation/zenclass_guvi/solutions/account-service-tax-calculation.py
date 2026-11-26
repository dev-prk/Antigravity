import sys

data = sys.stdin.read().strip().split()
if len(data) < 5:
    print("")
    sys.exit(0)

account_type = int(data[0])
holder_name = data[1]
account_number = data[2]
balance = float(data[3])
amount = float(data[4])

if account_type == 1:
    tax_rate = 20.0 / 100.0
elif account_type == 2:
    tax_rate = 10.0 / 100.0
elif account_type == 3:
    tax_rate = 5.0 / 100.0
else:
    tax_rate = 0.0

tax = amount * tax_rate
transferred = amount + tax
remaining = balance - transferred

remaining = round(remaining, 2)
print(f"Your remaining balance is Rs.{remaining:.2f}")
