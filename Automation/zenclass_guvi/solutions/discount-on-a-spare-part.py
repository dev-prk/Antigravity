price = int(input())
discount = int(input())

discount_amount = price * discount / 100
final_price = price - discount_amount

print(f"{discount_amount:.2f}")
print(f"{final_price:.2f}")
