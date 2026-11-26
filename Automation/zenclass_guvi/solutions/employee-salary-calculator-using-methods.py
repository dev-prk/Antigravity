def calculate_hra(basic_salary):
    return int(0.2 * basic_salary)

def calculate_da(basic_salary):
    return int(0.1 * basic_salary)

def calculate_gross_salary(basic_salary):
    return basic_salary + calculate_hra(basic_salary) + calculate_da(basic_salary)

def display_results(hra, da, gross_salary):
    print(f"HRA: {hra}")
    print(f"DA: {da}")
    print(f"Gross Salary: {gross_salary}")

def main():
    basic_salary = int(input().strip())
    hra = calculate_hra(basic_salary)
    da = calculate_da(basic_salary)
    gross_salary = calculate_gross_salary(basic_salary)
    display_results(hra, da, gross_salary)

if __name__ == "__main__":
    main()
