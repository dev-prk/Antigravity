import sys
import calendar

def solve():
    months = {
        'January': 31, 'February': 28, 'March': 31, 'April': 30,
        'May': 31, 'June': 30, 'July': 31, 'August': 31,
        'September': 30, 'October': 31, 'November': 30, 'December': 31
    }
    
    line = sys.stdin.readline().strip()
    if not line:
        return
    
    parts = line.split()
    month_name = parts[0].capitalize()
    year = int(parts[1])
    
    if month_name not in months:
        print(-1)
        return
    
    if month_name == 'February' and calendar.isleap(year):
        days_in_month = 29
    else:
        days_in_month = months[month_name]
    
    working_days = []
    for day in range(2, days_in_month + 1):
        factors = []
        for i in range(1, day + 1):
            if day % i == 0:
                factors.append(i)
        if len(factors) <= 2:
            working_days.append(day)
    
    print(len(working_days))

solve()
