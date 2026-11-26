months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']

date = input().strip()
parts = date.split('-')
month_num = int(parts[1])
print(months[month_num - 1])
