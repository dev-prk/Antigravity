import sys

def is_leap_year(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

def days_in_month(m, y):
    if m in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif m in [4, 6, 9, 11]:
        return 30
    elif m == 2:
        return 29 if is_leap_year(y) else 28
    return 0

def is_valid_date(d, m, y):
    if y < 1 or m < 1 or m > 12 or d < 1:
        return False
    return d <= days_in_month(m, y)

def increment_date(d, m, y):
    if d < days_in_month(m, y):
        return (d + 1, m, y)
    elif m < 12:
        return (1, m + 1, y)
    else:
        return (1, 1, y + 1)

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 3:
        print("Invalid")
        return
    try:
        d, m, y = map(int, data[:3])
    except:
        print("Invalid")
        return
    if is_valid_date(d, m, y):
        new_d, new_m, new_y = increment_date(d, m, y)
        print(f"{new_d} {new_m} {new_y}")
    else:
        print("Invalid")

if __name__ == "__main__":
    main()
