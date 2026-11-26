import sys

def main():
    months_31 = {'JANUARY', 'MARCH', 'MAY', 'JULY', 'AUGUST', 'OCTOBER', 'DECEMBER'}
    
    n = int(sys.stdin.readline().strip())
    line = sys.stdin.readline().strip()
    
    if n == 0 or not line:
        print(-1)
        return
    
    parts = line.split()
    employees = []
    for i in range(n):
        day = int(parts[i * 3])
        month = parts[i * 3 + 1].upper()
        year = int(parts[i * 3 + 2])
        employees.append((day, month, year))
    
    result = []
    for idx in range(n):
        day, month, year = employees[idx]
        year_int = int(year)
        if year_int <= 1987:
            if month in months_31:
                if year_int < 1987 or month != 'JULY' or day <= 22:
                    result.append(idx + 1)
    
    if not result:
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
