import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    tokens = data[1:]
    employees = []
    for i in range(n):
        name = tokens[2*i]
        salary = int(tokens[2*i+1])
        employees.append((salary, name))
    employees.sort(key=lambda x: x[0])
    out_lines = [name for _, name in employees]
    sys.stdout.write("\n".join(out_lines))

if __name__ == "__main__":
    main()
