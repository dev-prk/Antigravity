import sys

def is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

def main():
    s = sys.stdin.readline()
    s = s.strip()
    if len(s) != 10:
        print("no")
        return
    if s[2] != '/' or s[5] != '/':
        print("no")
        return
    day_str = s[0:2]
    month_str = s[3:5]
    year_str = s[6:10]
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        print("no")
        return
    day = int(day_str)
    month = int(month_str)
    year = int(year_str)
    if not (1 <= month <= 12):
        print("no")
        return
    if day < 1:
        print("no")
        return
    if month in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif month in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 29 if is_leap(year) else 28
    if day > max_day:
        print("no")
        return
    print("yes")

if __name__ == "__main__":
    main()
