import sys

def main():
    units = int(sys.stdin.readline().strip())
    
    if units <= 100:
        total_bill = units * 2
    elif units <= 200:
        total_bill = 100 * 2 + (units - 100) * 3
    else:
        total_bill = 100 * 2 + 100 * 3 + (units - 200) * 5
    
    avg_cost = total_bill // units if units > 0 else 0
    units_above_200 = max(0, units - 200)
    
    print(f"Total Bill: {total_bill}")
    print(f"Average Cost Per Unit: {avg_cost}")
    print(f"Units Above 200: {units_above_200}")

if __name__ == "__main__":
    main()
