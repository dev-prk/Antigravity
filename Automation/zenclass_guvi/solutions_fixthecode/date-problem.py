date = input()
dd, mm, yy = date.split(' ')
dd = int(dd)
mm = int(mm)
yy = int(yy)

def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_max_day(day, month, year):
    if month == 2:
        return 29 if is_leap_year(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31

if mm < 1 or mm > 12:
    print("Invalid")
else:
    max1 = get_max_day(dd, mm, yy)
    if dd < 1 or dd > max1:
        print("Invalid")
    elif dd == max1 and mm != 12:
        dd = 1
        mm = mm + 1
        print(dd, mm, yy)
    elif dd == 31 and mm == 12:
        dd = 1
        mm = 1
        yy = yy + 1
        print(dd, mm, yy)
    else:
        dd = dd + 1
        print(dd, mm, yy)
