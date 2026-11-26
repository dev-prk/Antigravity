import sys

def is_valid_date(date_str):
    parts = date_str.strip().split('/')
    if len(parts) != 3:
        return False
    if len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 4:
        return False
    try:
        dd = int(parts[0])
        mm = int(parts[1])
        yy = int(parts[2])
    except ValueError:
        return False
    if mm < 1 or mm > 12:
        return False
    if dd < 1:
        return False
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (yy % 4 == 0 and yy % 100 != 0) or (yy % 400 == 0):
        days_in_month[2] = 29
    if dd > days_in_month[mm]:
        return False
    return True

def main():
    line = sys.stdin.readline()
    if not line:
        print("Not valid")
        return
    date_str = line.strip()
    if is_valid_date(date_str):
        print("Valid")
    else:
        print("Not valid")

if __name__ == "__main__":
    main()
