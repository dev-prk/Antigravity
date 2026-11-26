# Read inputs according to input specification
# First input: float (principal)
# Second input: integer (time in years)
# Third input: float (rate in percent)
principal = float(input())
time = int(input())
rate = float(input())

# Calculate simple interest: (P * T * R) / 100
simple_interest = (principal * time * rate) / 100

# Print the simple interest
print(simple_interest)
