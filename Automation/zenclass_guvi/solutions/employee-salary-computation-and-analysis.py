import sys

def main():
    data = sys.stdin.read().strip()
    basic_salary = int(data) if data != "" else 0

    hra = basic_salary * 20 // 100
    da = basic_salary * 10 // 100
    gross_salary = basic_salary + hra + da
    annual_salary = gross_salary * 12

    print(f"HRA: {hra}")
    print(f"DA: {da}")
    print(f"Gross Salary: {gross_salary}")
    print(f"Annual Salary: {annual_salary}")

if __name__ == "__main__":
    main()
